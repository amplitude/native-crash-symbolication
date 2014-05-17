import handlers.main
import handlers.crash

ALL = [
  (r"/", handlers.main.LandingHandler),
  (r"/settings", handlers.main.SettingsHandler),

  (r"/app/(.+)", handlers.main.MainHandler),

#  (r"/libs/(\w+)", handlers.UploadLibHandler),
  (r"/crash", handlers.crash.UploadCrashHandler),
  (r"/1/libs/([-\w\.]+)", handlers.crash.RestUploadLibHandler),
  (r"/1/libs", handlers.crash.RestUploadLibHandler),
  (r"/1/reprocess", handlers.crash.RestReprocessCrashHandler),
  (r"/1/crashes", handlers.crash.RestExportCrashesHandler),
]
