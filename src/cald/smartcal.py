import datetime
import time
import threading
from icalendar import Calendar, Event, Alarm
import sys
import os
# Add the 'src' directory to the Python module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.speaker.speaker import Speaker

class MyCalendar(Speaker):
    def __init__(self):
        super().__init__()  # Initialize the parent Speaker class
        # Create an iCalendar object
        self.cal = Calendar()
        self.cal.add('prodid', '-//My Calendar Product//example.com//')
        self.cal.add('version', '2.0')
        
        # Used for monitoring threads and stopping them gracefully
        self.stop_event = threading.Event()
        self.threads = []
        self.notified = {}  # To track notified events (keyed by (date, uid))
        self.event_counter = 0  # To assign unique UIDs to events
        self.add_default_events()
        #Start the event monitoring in a separate thread.
        self.monitor_thread = threading.Thread(target=self.monitor_events, args=(1,))
        self.monitor_thread.start()        

    def add_event(self, dtstart, dtend, summary, description="", freq=None, count=20, alarm_time=20):
        """
        Add a one-time event.
        
        :param dtstart: datetime.datetime object for the start time.
        :param dtend: datetime.datetime object for the end time.
        :param summary: Title of the event.
        :param description: Description of the event.
        """
        event = Event()
        event.add('summary', summary)
        event.add('dtstart', dtstart)
        event.add('dtend', dtend)
        event.add('description', description)        
        if freq is not None and count > 0:
            # Add an RRULE to repeat the event daily 'count' times.
            # check if freq is daily,weekly, monthly or yearly
            if freq in ['daily', 'weekly', 'monthly', 'yearly']:
                event.add('rrule', {'freq': 'daily', 'count': count})
            elif freq == 'bi-weekly':
                event.add('rrule', {'freq': 'weekly', 'interval': 2, 'count': count})
        uid = f"event-{self.event_counter}@example.com"
        event.add('uid', uid)
        self.event_counter += 1
        # Add an alarm to the event
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', 'Reminder')
        #add trigger time as 1 minute before dtstart        
        alarm.add('trigger', dtstart - datetime.timedelta(minutes=alarm_time))
        event.add_component(alarm)
        self.cal.add_component(event) 

    def print_calendar(self):
        """
        Print all events stored in the iCalendar object.
        """
        print("Calendar Events:")
        for component in self.cal.walk():
            if component.name == "VEVENT":
                dtstart = component.get('dtstart').dt
                dtend = component.get('dtend').dt
                summary = component.get('summary')
                description = component.get('description')
                rrule = component.get('rrule')
                print("-----")
                print(f"Summary: {summary}")
                print(f"Start: {dtstart}")
                print(f"End: {dtend}")
                print(f"Description: {description}")
                if rrule:
                    print(f"Recurrence Rule: {rrule}")
        print("-----")

    def print_event_repeatedly(self, event):
        """
        Print an event's details every minute for 20 minutes (or until stopped).
        
        :param event: The icalendar event component.
        """
        count = 0
        summary = event.get('summary')
        description = event.get('description')
        #print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Starting event '{summary}' - {description}")
        while count < 20 and not self.stop_event.is_set():
            print(f"[Reminder {count+1}: {datetime.datetime.now().strftime('%H:%M:%S')}] Event '{summary}' - {description}")
            self.read_event_detail(f"Reminder {count+1}:  {summary}. {description}")
            count += 1
            # Sleep in one-second increments to check the stop flag.
            for _ in range(15):
                if self.stop_event.is_set():
                    break
                time.sleep(1)

    def monitor_events(self, check_interval=1):
        """
        Continuously check for events whose start time (minute precision) matches the current time.
        When an event is due, spawn a thread that prints the event details every minute for 20 minutes.
        """
        print("Starting event monitoring. Press Ctrl+C or call stop_all() to stop.")
        try:
            while not self.stop_event.is_set():
                now = datetime.datetime.now()
                today = now.date()
                current_time = now.time()
                calendar_component = None
                uid = None
                duration = 0
                
                for component in self.cal.walk():
                    if component.name == "VEVENT":
                        dtstart = component.get('dtstart').dt
                        # For this example, we assume dtstart is a datetime
                        if isinstance(dtstart, datetime.date) and not isinstance(dtstart, datetime.datetime):
                            # If only a date is provided, assume the event starts at midnight.
                            dtstart = datetime.datetime.combine(dtstart, datetime.time())
                        event_time = dtstart.time()
                        uid = component.get('uid')
                        duration = component.get('dtend').dt - dtstart
                        calendar_component = component
                        
                        # Check if the current time (hour and minute) matches the event's start time.
                    elif component.name == "VALARM":                        
                        trigger = component.get('trigger').dt
                        event_time_with_alarm = trigger
                        #print(f"Event time with alarm: {event_time_with_alarm}")
                        if (now >= event_time_with_alarm and 
                            now < event_time_with_alarm + duration):
                            key = (today, uid)
                            if key not in self.notified:
                                t = threading.Thread(target=self.print_event_repeatedly, args=(calendar_component,))
                                t.start()
                                self.threads.append(t)
                                self.notified[key] = True
                time.sleep(check_interval)
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected. Stopping event monitoring.")
            self.stop_all()    

    def stop_repeating_threads(self):
        """
        Stop the repeating event monitoring thread.
        
        :param event: The icalendar event component.
        """
        print("Stopping all threads...")
        self.stop_event.set()
        for t in self.threads:
            #print(f"Waiting for thread {t} to finish...")
            t.join()

    def stop_all(self):
        """
        Signal all threads to stop and wait for them to finish.
        """
        self.stop_repeating_threads()
        if self.monitor_thread:
            self.monitor_thread.join()
        print("All threads stopped.")

    #Read the Event Detail
    def read_event_detail(self, event_text):
        """
        Speak the event's details.
        
        :param event_text: The text to speak.
        """
        # Use a text-to-speech engine to speak the event details.
        print(f"Speaking event: {event_text}")
        self.play_text(event_text) 
        # Add code here to speak the event text.

    def add_default_events(self):
        """
        Add default events to the calendar.
        """
        
        now = datetime.datetime.now()
        
        # Define the first occurrence: choose a Tuesday date (e.g., April 8, 2025)
        dtstart = datetime.datetime(2025, 3, 31, 19, 00, 0)  # Monday, 7:00 PM
        dtend = dtstart + datetime.timedelta(minutes=60)     # 30 minutes duration
        self.add_event(dtstart, dtend, "Bi Lin Chinese Course", "Hello Eric, Please prepare the ipad to join the Chinese course", "weekly", alarm_time=10)

        # 
        dtstart = datetime.datetime(2025, 4, 1, 18, 00, 00)  # Tuesday, 6:00 PM
        dtend = dtstart + datetime.timedelta(minutes=60)     # 60 minutes duration
        self.add_event(dtstart, dtend, "CC English Course", "Hello Eric, Please prepare to go to CC to join the English course", "weekly", alarm_time=20)

        #Every Friday at 3pm for piano classs
        dtstart = datetime.datetime(2025, 4, 4, 15, 00, 00)  # Friday, 3:00 PM
        dtend = dtstart + datetime.timedelta(minutes=60)     # 60 minutes duration
        self.add_event(dtstart, dtend, "Piano Class", "Hello Eric, Please prepare to go to Boon Keng for your Piano class", "weekly", alarm_time=40)

        #Every Wensday at 5pm for hellen's Piano classs
        dtstart = datetime.datetime(2025, 4, 2, 17, 00, 00)  # Wensday, 5:00 PM
        dtend = dtstart + datetime.timedelta(minutes=60)     # 60 minutes duration
        self.add_event(dtstart, dtend, "Hellen's Piano Class", "Hello Hellen, Please prepare to go to Boon Keng for your Piano class", "weekly", alarm_time=40)
        
        #Every Saturday at 9am for football class
        dtstart = datetime.datetime(2025, 4, 5, 9, 00, 00)  # Saturday, 9:00 AM
        dtend = dtstart + datetime.timedelta(minutes=60)     # 60 minutes duration
        self.add_event(dtstart, dtend, "Football Class", "Hello Eric, Please prepare to go to St Stepen school for your Football class", "weekly", alarm_time=60)

        # Example daily repeating event: scheduled 15 seconds from now, lasts 15 minutes, repeats daily for 20 occurrences.
        # dtstart_daily = now + datetime.timedelta(seconds=15)
        # dtend_daily = dtstart_daily + datetime.timedelta(minutes=30)
        # self.add_event(dtstart_daily, dtend_daily, "Daily Standup", "Daily team sync-up meeting.", "daily")
        
        # Print the current calendar events
        self.print_calendar() 

if __name__ == "__main__":
    
    my_cal = MyCalendar()
    
    # Define start_time to track elapsed time
    start_time = time.time()
    
    # Keep the main thread alive until a KeyboardInterrupt is received.
    try:
        while True:
            time.sleep(1)
            # Call stop_repeating_threads after 25 seconds
            #            if time.time() - start_time > 25:
            #                my_cal.stop_repeating_threads()
    except KeyboardInterrupt:
        print("\nMain thread received KeyboardInterrupt. Stopping all threads.")
        my_cal.stop_event.set()  # Signal all threads to stop
        my_cal.stop_all()  # Ensure all threads are joined properly
