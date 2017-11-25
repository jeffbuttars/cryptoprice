import app
import logging


logger = logging.getLogger(__name__)

#  import os
#  from optparse import OptionParser


#  opt_parser = OptionParser(
#      usage=("usage: %prog Crypto Currency Slackbot.")
#  )

#  # A basic option that sets an option variable to a string value
#  opt_parser.add_option(
#      "-d", "--debug", dest="debug",
#      default=False, action='store_true',
#      help=("Enable debugging")
#  )

#  opt_parser.add_option(
#      "-c", "--client-id", dest="client_id",
#      default=os.environ.get('CLIENT_ID', ''),
#      help=("API Client ID")
#  )

#  opt_parser.add_option(
#      "-s", "--client-secret", dest="client_secret",
#      default=os.environ.get('CLIENT_SECRET', ''),
#      help=("API Client Secret")
#  )

#  opt_parser.add_option(
#      "-t", "--verification-token", dest="verification_token",
#      default=os.environ.get('VERIFICATION_TOKEN', ''),
#      help=("API Client Verification Token")
#  )

#  opt_parser.add_option(
#      "-r", "--redis-url", dest="redis_url",
#      default=os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'),
#      help=("Redis URL")
#  )

#  (options, _) = opt_parser.parse_args()


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    app.app.run(debug=True)
