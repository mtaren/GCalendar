#!/usr/bin/env python

MAIN_CALANDAR = 'gcali' # clandar to add events to
CALANDAR		= ['workout', 'gcali', 'School Stuff', 'archive', 'FOOD'] #calandars to monitor
#CALANDAR		= ['gcali', 'archive'] #calandars to monitor
ARCHIVECAL = 'archive'
__program__		 = 'gcalcli'
__version__		 = 'v3.1'
__author__		  = 'Eric Davis, Brian Hartvigsen'

__API_CLIENT_ID__ = 'fill_in'
__API_CLIENT_SECRET__ = 'fill_in'


# These are standard libraries and should never fail
import sys, os, re, gflags, shlex, time

import locale, textwrap, signal
from Queue import Queue
from datetime import datetime, timedelta, date
import traceback
#import included gui
import Reminder as rem

# Required 3rd partie libraries
try:
	from dateutil.tz import *
	from dateutil.parser import *
	from dateutil.rrule import *
	import httplib2
	from apiclient.discovery import build
	from oauth2client.file import Storage
	from oauth2client.client import OAuth2WebServerFlow
	from oauth2client.tools import run
	import winsound
except ImportError, e:
	print "ERROR: Missing module - %s" % e.args[0]
	sys.exit(1)

import json
from dateutil.relativedelta import relativedelta

class parsedatetime:
	class Calendar:
		def parse(self, string):
			return ([], 0)




def PrintErrMsg(msg):
	PrintMsg(CLR_BRRED(), msg)

def PrintMsg(color, msg):
	sys.stdout.write(msg)

def DebugPrint(msg):
	return
	PrintMsg(CLR_YLW(), msg)

def dprint(obj):
	try:
		from pprint import pprint
		pprint(obj)
	except ImportError, e:
		print obj


class DateTimeParser:
	def __init__(self):
		self.pdtCalendar = parsedatetime.Calendar()

	def fromString(self, eWhen, useMidnight=True):
		if useMidnight:
			defaultDateTime = datetime.now(tzlocal()).replace(hour=0,
													 minute=0,
													 second=0,
													 microsecond=0)
		else:
			defaultDateTime = datetime.now(tzlocal())

		try:
			eTimeStart = parse(eWhen, default=defaultDateTime)
		except:
			struct, result = self.pdtCalendar.parse(eWhen)
			if not result:
				raise ValueError("Date and time is invalid")
			eTimeStart = datetime.fromtimestamp(time.mktime(struct), tzlocal())


		return eTimeStart


def GetTimeFromStr(eWhen, eDuration=0):
	dtp = DateTimeParser()

	try:
		eTimeStart = dtp.fromString(eWhen)
	except:
		PrintErrMsg('Date and time is invalid!\n')
		sys.exit(1)

	try:
		eTimeStop = eTimeStart + timedelta(minutes=float(eDuration))
	except:
		PrintErrMsg('Duration time (minutes) is invalid\n')
		sys.exit(1)

	sTimeStart = eTimeStart.isoformat()
	sTimeStop = eTimeStop.isoformat()

	return sTimeStart, sTimeStop


class gcalcli:

	cache		 = {}
	refreshCache  = True
	useCache	  = False
	allCals	   = []
	archiveCal = None
	allEvents	 = []
	cals		  = []
	now		   = datetime.now(tzlocal())
	agendaLength  = 5
	authHttp	  = None
	calService	= None
	urlService	= None
	military	  = False
	ignoreStarted = False
	calWidth	  = 10
	calMonday	 = False
	command	   = 'notify-send -u critical -a gcalcli %s'
	tsv		   = False
	dateParser	= DateTimeParser()

	detailCalendar   = False
	detailLocation   = False
	detailLength	 = False
	detailReminders  = False
	detailDescr	  = False
	detailDescrWidth = 80
	detailUrl		= None

	ACCESS_OWNER	= 'owner'
	ACCESS_WRITER   = 'writer'
	ACCESS_READER   = 'reader'
	ACCESS_FREEBUSY = 'freeBusyReader'

	def __init__(self,
				 calNames=[],
				 calNameColors=[],
				 military=False,
				 detailCalendar=False,
				 detailLocation=False,
				 detailLength=False,
				 detailReminders=False,
				 detailDescr=False,
				 detailDescrWidth=80,
				 detailUrl=None,
				 ignoreStarted=False,
				 calWidth=10,
				 calMonday=False,
				 tsv=False,
				 refreshCache=False,
				 useCache=False,
				 configFolder=None,
				 client_id=__API_CLIENT_ID__,
				 client_secret=__API_CLIENT_SECRET__):

		self.military	  = military
		self.ignoreStarted = ignoreStarted
		self.calWidth	  = calWidth
		self.calMonday	 = calMonday
		self.tsv		   = tsv
		self.refreshCache  = refreshCache
		self.useCache	  = useCache

		self.detailCalendar   = detailCalendar
		self.detailLocation   = detailLocation
		self.detailLength	 = detailLength
		self.detailReminders  = detailReminders
		self.detailDescr	  = detailDescr
		self.detailDescrWidth = detailDescrWidth
		self.detailUrl		= detailUrl

		self.configFolder	 = configFolder

		self.client_id		= client_id
		self.client_secret	= client_secret

		self._GetCalandars()

		for cal in self.allCals:
			if len(calNames):
				for i in xrange(len(calNames)):
					if re.search(calNames[i].lower(), cal['summary'].lower()):
						self.cals.append(cal)
						cal['colorSpec'] = calNameColors[i]
			else:
				self.cals.append(cal)
				cal['colorSpec'] = None


	def _GoogleAuth(self):
		if not self.authHttp:
			if self.configFolder:
				storage = Storage(os.path.expanduser("%s/oauth" % self.configFolder))
			else:
				storage = Storage(os.path.expanduser('~/.gcalcli_oauth'))
			credentials = storage.get()
			#credentials = None

			if credentials is None or credentials.invalid == True:
				credentials = run(
					OAuth2WebServerFlow(
						client_id=self.client_id,
						client_secret=self.client_secret,
						scope=['https://www.googleapis.com/auth/calendar',
							   'https://www.googleapis.com/auth/urlshortener'],
						user_agent=__program__+'/'+__version__),
					storage)

			self.authHttp = credentials.authorize(httplib2.Http())

		return self.authHttp


	def _CalService(self):
		if not self.calService:
			self.calService = \
				 build(serviceName='calendar',
					   version='v3',
					   http=self._GoogleAuth())

		return self.calService


	def _UrlService(self): #dont need
		if not self.urlService:
			self._GoogleAuth()
			self.urlService = \
				 build(serviceName='urlshortener',
					   version='v1',
					   http=self._GoogleAuth())

		return self.urlService

	def _GetCalandars(self):
		self.allCals   = []
		self.allEvents = []
		
		calList = self._CalService().calendarList().list().execute()

		while True:
			for cal in calList['items']:
				if cal['summary'] in CALANDAR: # only look at your calandars
					if cal['summary'] == MAIN_CALANDAR:
						self.allCals.insert(0,cal) #makes gcali the first calandar
					else: 
						if cal['summary'] == ARCHIVECAL:# dont trigger on archivecal events
							self.archiveCal = cal
							print 'found archive cal'
						else:
							self.allCals.append(cal)
			pageToken = calList.get('nextPageToken')
			if pageToken:
				calList = self._CalService().calendarList().\
						  list(pageToken = pageToken).execute()
			else:
				break

		# gcalcli defined way to order calendars
		order = { self.ACCESS_OWNER	: 1,
				  self.ACCESS_WRITER   : 2,
				  self.ACCESS_READER   : 3,
				  self.ACCESS_FREEBUSY : 4 }

		self.allCals.sort(lambda x, y:
						   cmp(order[x['accessRole']],
							   order[y['accessRole']]))

		for cal in self.allCals:
			
			#events = self._CalService().events().\
			#		 list(calendarId = cal['id'],
			#			  singleEvents = False).execute()
			#get todays events only!
			start = self.now.replace(hour=0,
										 minute=0,
										 second=0,
										 microsecond=0)
			start = start + timedelta(days= -1)
			end = (start + timedelta(days=3))
			events = self._CalService().events().\
					   list(calendarId = cal['id'],
							timeMin = start.isoformat() if start else None,
							timeMax = end.isoformat() if end else None,
							singleEvents = False).execute()

				#th = threading.Thread(target=worker, args=(cal, work))
				#threads.append(th)
				#th.start()
				

			while True:
				if 'items' not in events:
					break

				for event in events['items']:

					event['gcalcli_cal'] = cal

					if 'status' in event and event['status'] == 'cancelled':
						continue

					if 'dateTime' in event['start']:
						#print event['start']['dateTime']
						print event['start']['dateTime']
						#temp = event['start']['dateTime'] + timedelta(days = 1)
						#print 'temp is'
						#print temp
						event['s'] = parse(event['start']['dateTime'])
					#	print event['s']
					#	print event['s'].strftime("%Y-%m-%dT%H:%M")
						#event['s'] = event['start']['dateTime']
						#print event['s']
					else:
						# all day events
						continue
						event['s'] = parse(event['start']['date'])

					if event['s'].tzinfo == None:
						event['s'] = event['s'].replace(tzinfo=tzlocal())
					else:
						event['s'] = event['s'].astimezone(tzlocal())

					if 'dateTime' in event['end']:
						event['e'] = parse(event['end']['dateTime'])
					else:
						# all day events
						event['e'] = parse(event['end']['date'])

					if event['e'].tzinfo == None:
						event['e'] = event['e'].replace(tzinfo=tzlocal())
					else:
						event['e'] = event['e'].astimezone(tzlocal())

					# http://en.wikipedia.org/wiki/Year_2038_problem
					# Catch the year 2038 problem here as the python dateutil
					# module can choke throwing a ValueError exception. If
					# either the start or end time for an event has a year
					# '>= 2038' dump it.
					if event['s'].year >= 2038 or event['e'].year >= 2038:
						continue

					self.allEvents.append(event)

				pageToken = events.get('nextPageToken')
				if pageToken:
					events = self._CalService().events().\
							 list(calendarId = cal['id'],
								  singleEvents = False,
								  pageToken = pageToken).execute()
				else:
					break

		# sort all events across all calendars together
		self.allEvents.sort(lambda x, y: cmp(x['s'], y['s']))

	
	def _ShortenURL(self, url):
		if self.detailUrl != "short":
			return url
		# Note that when authenticated to a google account different shortUrls
		# can be returned for the same longUrl. See: http://goo.gl/Ya0A9
		shortUrl = self._UrlService().url().insert(body={'longUrl':url}).execute()
		return shortUrl['id']


	def _ValidTitle(self, event):
		if 'summary' in event and event['summary'].strip():
			return event['summary']
		else:
			return "(No title)"





	def _PrintEvent(self, event, prefix):
		print "----------Event--------"
		indent = 10 * ' '
		detailsIndent = 19 * ' '

		if self.military:
			timeFormat = '%-5s'
			tmpTimeStr = event['s'].strftime("%H:%M")
		else:
			timeFormat = '%-7s'
			tmpTimeStr = \
				event['s'].strftime("%I:%M").lstrip('0').rjust(5) + \
				event['s'].strftime('%p').lower()

		if not prefix:
			prefix = indent

		#PrintMsg(self.dateColor, prefix)
		""" HERE is the start time"""
		""" event['s'] also gives yr starttime-endtime"""
		#print event['s'].strftime("%H:%M") #military time
		print event['s'].strftime("%I:%M") #notmilitary time
		#print event['s']
		"""HERE prints the date, Sat Jul 26"""
		#print prefix
		if event['s'].hour == 0 and event['s'].minute == 0 and \
		   event['e'].hour == 0 and event['e'].minute == 0:
			fmt = '  ' + timeFormat + '  %s\n'
			#PrintMsg(self._CalendarColor(event['gcalcli_cal']), fmt %
			#		 ('', self._ValidTitle(event).strip()))
			##ALL day events
			""" HERE is where you print summary for all day events"""
			print self._ValidTitle(event).strip()
		else:
			fmt = '  ' + timeFormat + '  %s\n'
#			if 'summary' not in event:
#				dprint(event)
#				dprint(event)
#	PrintMsg(self._CalendarColor(event['gcalcli_cal']), fmt %
#			 (tmpTimeStr, self._ValidTitle(event).strip()))
			"""      HERE is how to print event summar """
			print self._ValidTitle(event).strip()
		return
	def _DeleteEvent(self, event):
		print "delete me"
		if True:
			self._CalService().events().\
				 delete(calendarId = event['gcalcli_cal']['id'],
						eventId = event['id']).execute()
			#PrintMsg(CLR_RED(), "Deleted!\n")
			return

		#PrintMsg(CLR_MAG(), "Delete? [N]o [y]es [q]uit: ")
		#val = raw_input()

		if not val or val.lower() == 'n':
			return

		elif val.lower() == 'y':
			self._CalService().events().\
				 delete(calendarId = event['gcalcli_cal']['id'],
						eventId = event['id']).execute()
			#PrintMsg(CLR_RED(), "Deleted!\n")

		elif val.lower() == 'q':
			sys.stdout.write('\n')
			sys.exit(0)

		else:
			#PrintErrMsg('Error: invalid input\n')
			sys.stdout.write('\n')
			sys.exit(1)
	def ChangeTime(self, event, val):
		print "EVENT COLOR"
		#print event['colorId']
		val = val.strftime("%Y-%m-%dT%H:%M")
		if val.strip():
			td = (event['e'] - event['s'])
			length = ((td.days * 1440) + (td.seconds / 60))
			newStart, newEnd = GetTimeFromStr(val.strip(), length)
			event['s'] = parse(newStart)
			event['e'] = parse(newEnd)
			event['start'] = \
				{ 'dateTime' : newStart,
				  'timeZone' : event['gcalcli_cal']['timeZone'] }
			event['end'] = \
				{ 'dateTime' : newEnd,
				  'timeZone' : event['gcalcli_cal']['timeZone'] }
		modEvent = {}
		keys = ['summary', 'location', 'start', 'end',
				'reminders', 'description']
		for k in keys:
			if k in event:
				modEvent[k] = event[k]
				#modEvent['colorId'] = {'colorId' : '#2952A3'}
				modEvent['colorId'] = {'colorId' : '#ff0000'}

				
		success = False
		while success != True:
			try:
				self._CalService().events().\
				patch(calendarId = event['gcalcli_cal']['id'],
					eventId = event['id'],
					body = modEvent).execute()
				success = True
			except Exception as e:
				winsound.PlaySound('bells.wav', winsound.SND_FILENAME)
				print 'ack! an exception! Changetime'
			
			
		
	def DismissEvent(self, event): #moves it to the archive calandar
		success = False
		while success != True:
			try:
				self._CalService().events().\
					move(calendarId = event['gcalcli_cal']['id'],#event['gcalcli_cal']['id'],
						eventId = event['id'],
						destination = self.archiveCal['id']).execute()
				success = True
			except Exception as e:
				winsound.PlaySound('bells.wav', winsound.SND_FILENAME)
				print 'ack! an exception! DismissEvent'
		
		return
		
	def DelayEvent(self, event, listoftimes):
		print 'implement delay of event'
		current_time = datetime.now()
		end_time = current_time + relativedelta(minutes = listoftimes[0], hours = listoftimes[1], days = listoftimes[2], weeks = listoftimes[3], months = listoftimes[4])
		
		self.ChangeTime(event, end_time)

	def _IterateEvents(self, startDateTime, eventList,
					   yearDate=False, work=None):

		if len(eventList) == 0:
			PrintMsg(CLR_YLW(), "\nNo Events Found...\n")
			return

		# 10 chars for day and length must match 'indent' in _PrintEvent
		dayFormat = '\n%F' if yearDate else '\n%a %b %d'
		day = ''

		for event in eventList:

			if self.ignoreStarted and (event['s'] < startDateTime):
				continue

			prefix = event['s']
			#tmpDayStr = event['s'].strftime(dayFormat)
			#prefix	= None
			#if yearDate or tmpDayStr != day:
			#	day = prefix = tmpDayStr

			self._PrintEvent(event, prefix)

			if work:
				work(event)


	def _GetAllEvents(self, cal, events, end):

		eventList = []

		while 1:
			if 'items' not in events:
				break

			for event in events['items']:

				event['gcalcli_cal'] = cal

				if 'status' in event and event['status'] == 'cancelled':
					continue

				if 'dateTime' in event['start']:
					event['s'] = parse(event['start']['dateTime'])
				else:
					event['s'] = parse(event['start']['date']) # all date events

				if event['s'].tzinfo == None:
					event['s'] = event['s'].replace(tzinfo=tzlocal())
				else:
					event['s'] = event['s'].astimezone(tzlocal())

				if 'dateTime' in event['end']:
					event['e'] = parse(event['end']['dateTime'])
				else:
					event['e'] = parse(event['end']['date']) # all date events

				if event['e'].tzinfo == None:
					event['e'] = event['e'].replace(tzinfo=tzlocal())
				else:
					event['e'] = event['e'].astimezone(tzlocal())

				# For all-day events, Google seems to assume that the event time
				# is based in the UTC instead of the local timezone.  Here we
				# filter out those events start beyond a specified end time.
				if end and (event['s'] >= end):
					continue

				# http://en.wikipedia.org/wiki/Year_2038_problem
				# Catch the year 2038 problem here as the python dateutil module
				# can choke throwing a ValueError exception. If either the start
				# or end time for an event has a year '>= 2038' dump it.
				if event['s'].year >= 2038 or event['e'].year >= 2038:
					continue

				eventList.append(event)

			pageToken = events.get('nextPageToken')
			if pageToken:
				events = self._CalService().events().\
						 list(calendarId = cal['id'],
							  pageToken = pageToken).execute()
			else:
				break

		return eventList


	def _SearchForCalEvents(self, start, end, searchText):

		eventList = []

		queue = Queue()
		threads = []

		def worker(cal, work):
			events = work.execute()
			queue.put((cal, events))

		for cal in self.cals:
			if cal['summary'] in CALANDAR:
				work = self._CalService().events().\
					   list(calendarId = cal['id'],
							timeMin = start.isoformat() if start else None,
							timeMax = end.isoformat() if end else None,
							q = searchText if searchText else None,
							singleEvents = True)

				#th = threading.Thread(target=worker, args=(cal, work))
				#threads.append(th)
				#th.start()
				events = work.execute()
				queue.put((cal, events))

		#for th in threads:
		#	th.join()

		while not queue.empty():
			cal, events = queue.get()
			eventList.extend(self._GetAllEvents(cal, events, end))

		eventList.sort(lambda x, y: cmp(x['s'], y['s']))
		return eventList


	def ListAllCalendars(self):

		accessLen = 0

		for cal in self.allCals:
			length = len(cal['accessRole'])
			if length > accessLen: accessLen = length

		if accessLen < len('Access'): accessLen = len('Access')

		format = ' %0' + str(accessLen) + 's  %s\n'
		print "Access   Title"
		print "------   -----"

		for cal in self.allCals:
			#PrintMsg(self._CalendarColor(cal), format % (cal['accessRole'], cal['summary']))
			print cal['accessRole'] + "     " + cal['summary']
		print "done"

	def GetTodaysEvents(self):
		start = self.now.replace(hour=0,
										 minute=0,
										 second=0,
										 microsecond=0)
		end = (start + timedelta(days=2))
		return		self._SearchForCalEvents(start, end, None)

	def DeleteEvents(self, searchText='', expert=False):

		# the empty string would get *ALL* events...
		if searchText == '':
			return

		eventList = self._SearchForCalEvents(None, None, searchText)

		self.iamaExpert = expert
		self._IterateEvents(self.now, eventList,
							yearDate=True, work=self._DeleteEvent)

	def AddEvent(self, eTitle, eStart, eEnd, calandarID, eWhere=None,eDescr=None, reminder = None):

		#if len(self.cals) != 1:
		#	PrintErrMsg("Must specify a single calendar\n")
		#	return

		event = {}
		event['summary'] = unicode(eTitle, locale.getpreferredencoding() or "UTF-8")
		event['start']   = { 'dateTime' : eStart,
							 'timeZone' : self.cals[0]['timeZone'] }
		event['end']	 = { 'dateTime' : eEnd,
							 'timeZone' : self.cals[0]['timeZone'] }
		if eWhere:
			event['location'] = unicode(eWhere, locale.getpreferredencoding() or "UTF-8")
		if eDescr:
			event['description'] = unicode(eDescr, locale.getpreferredencoding() or "UTF-8")
		if reminder:
			event['reminders'] = {'useDefault' : False,
								  'overrides'  : [{'minutes' : reminder,
												   'method'  : 'popup'}]}
		print event
		success = False
		while success != True:
			try:
				newEvent = self._CalService().events().\
				   insert(calendarId = calandarID,
						  body = event).execute()
				success = True
			except Exception as e:
				#exc_type, exc_value, exc_traceback = sys.exc_info()
				winsound.PlaySound('bells.wav', winsound.SND_FILENAME)	
				#traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
				#print "*** print_exception:"
				#traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
				print 'insert exception'
				
		#if self.detailUrl:
		#	hLink = self._ShortenURL(newEvent['htmlLink'])
		#	PrintMsg(CLR_GRN(), 'New event added: %s\n' % hLink)

	
FLAGS = gflags.FLAGS

def MainMethod():
	
	dueEvents = []
	gcal = gcalcli() #initialize the gcali object, get today's calandars and events
	#to change days, now = different day, see getcalandar function
	current_time = datetime.now(tzlocal())# This is the date it starts looking for events, variable used only to be printed
	plus1hr = current_time +timedelta(hours=1) # add one hour
	plus1day = current_time + timedelta(hours= 1, days= 1)
	print str(current_time.time()) + "this is the timce"
	for event in gcal.allEvents:
		#print event['summary']
		#print event['s'].strftime("%H:%M") #military time
		print event['summary'] + " at ",
		print event['s'].time(),
		print 'vs',
		print current_time.time()
		if event['s'] < current_time:
			dueEvents.append(event)
			print event['summary']
	print "-----------List of Due events-----------"
	for event in dueEvents:
		print event['summary']
		
		#Uncomment this if the event is not showing up on calandar, but shows on gcali
		#gcal._DeleteEvent(event)  #Delete event here if it does not show up on google calandar website
		
		##----------------- Recurrance testbox
		#if  'recurrence' in event:
		#	print 'recurrance rule =' + str(event["recurrence"][0])
		#	datestart = event['s'].replace(day = current_time.day, month = current_time.month, year = current_time.year).strftime("%Y%m%dT%H%M%S")
		#	#datestart = parse(event['originalStartTime']['dateTime']).strftime("%Y%m%dT%H%M%S")
			 
		#	realrule = 'DTSTART:'+ datestart + ' '	+event["recurrence"][0]+ ';COUNT=4'
		#	print realrule
		#	nextdate = list(rrulestr(realrule))
		#	print nextdate[1]
		#	gcal.ChangeTime(event, nextdate[1])
			##-------------------------End reccurrance testing----------------------------###
			#plus1hr, blah = GetTimeFromStr(str(plus1hr))
			#plus1hr = str(plus1hr)[0:19] + str(plus1hr)[-6:]
		print "-----------------------DFASDF"
		listoftimes, action = rem.Create_reminder(event) #listof times is user input
		current_time = datetime.now()
	
		if  'recurrence' in event:
			datestart = event['s'].replace(day = current_time.day, month = current_time.month, year = current_time.year).strftime("%Y%m%dT%H%M%S")
			realrule = 'DTSTART:'+ datestart + ' '	+event["recurrence"][0]+ ';COUNT=4'
			nextdate = list(rrulestr(realrule)) #find instance of next reoccouring event
			gcal.ChangeTime(event, nextdate[1]) ## gets rid of today's reoccouring event 
			if action == 'Delay': 
				new_start = current_time + relativedelta(minutes = listoftimes[0], hours = +listoftimes[1], days = listoftimes[2], weeks = listoftimes[3], months = listoftimes[4])
				new_end = new_start + timedelta(hours = 1)
				gcal.AddEvent( str(event['summary']), new_start.strftime("%Y-%m-%dT%H:%M:%S"), new_end.strftime("%Y-%m-%dT%H:%M:%S"), event['gcalcli_cal']['id'])
				print 'implement add Event'
			elif action == 'Delete':
					gcal._DeleteEvent(event)
		else: #not a reoccouring event
			if action == 'Delay':
				gcal.DelayEvent(event, listoftimes)
			elif action == 'Delete':
				gcal._DeleteEvent(event)
			else:
				gcal.DismissEvent(event)
				
	
	
	
	#how to add an event
	current_time = datetime.now() - timedelta(minutes = 1)
	print gcal.cals[0]['id']
	"""gcal.AddEvent( 'detailedEvent', current_time.strftime("%Y-%m-%dT%H:%M:%S"), plus1hr.strftime("%Y-%m-%dT%H:%M:%S"),gcal.cals[0]['id'])
	#gcal.AddEvent( 'detailedEvent', current_time.strftime("%Y-%m-%dT%H:%M:%S"), plus1hr.strftime("%Y-%m-%dT%H:%M:%S"),gcal.cals[0]['id'])
	#gcal.AddEvent( 'detailedEvent', current_time.strftime("%Y-%m-%dT%H:%M:%S"), plus1hr.strftime("%Y-%m-%dT%H:%M:%S"),gcal.cals[0]['id'])
	gcal.AddEvent( 'detailedEvent', current_time.strftime("%Y-%m-%dT%H:%M:%S"), plus1hr.strftime("%Y-%m-%dT%H:%M:%S"),gcal.cals[0]['id'])
	gcal.AddEvent( 'detailedEvent', current_time.strftime("%Y-%m-%dT%H:%M:%S"), plus1hr.strftime("%Y-%m-%dT%H:%M:%S"),gcal.cals[0]['id'])
	gcal.AddEvent( 'detailedEvent', current_time.strftime("%Y-%m-%dT%H:%M:%S"), plus1hr.strftime("%Y-%m-%dT%H:%M:%S"),gcal.cals[0]['id'])
	gcal.AddEvent( 'detailedEvent', current_time.strftime("%Y-%m-%dT%H:%M:%S"), plus1hr.strftime("%Y-%m-%dT%H:%M:%S"),gcal.cals[0]['id'])
	gcal.AddEvent( 'detailedEvent', current_time.strftime("%Y-%m-%dT%H:%M:%S"), plus1hr.strftime("%Y-%m-%dT%H:%M:%S"),gcal.cals[0]['id'])
	"""
		#print event
	#	event['start'] = \
	#			{ 'dateTime' : plus1hr,
	#			  'timeZone' : event['gcalcli_cal']['timeZone'] }
		#gcal._CalService().events().patch(calendarId = event['gcalcli_cal']['id'], eventId = event['id'],body = event).execute()
		#gcal._CalService().events().insert(calendarId = event['gcalcli_cal']['id'], body = event).execute()
	

def SIGINT_handler(signum, frame):
	PrintErrMsg('Signal caught, bye!\n')
	sys.exit(1)

signal.signal(signal.SIGINT, SIGINT_handler)

if __name__ == '__main__':
	while True:
		
		try:
			MainMethod()
			
		except httplib2.ServerNotFoundError:
			print 'server not found-> sleeping for 3 seconds'
			#raw_input()
			time.sleep(3)
			continue
		except Exception as e:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			print "*** print_tb:"
			traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
			print "*** print_exception:"
			traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
			print e
			#if e == ServerNotFoundError:
			#	raw_input()
			continue
	#		rem.Create_popup()
	#		print 'ack! an exception!'
			
		time.sleep(4.5*60) #sleep 4.5 minutes

