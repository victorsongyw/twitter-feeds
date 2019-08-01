####################################
#    Author: Yiwen(Victor) Song    #
####################################

Supported Platforms:
	+ Mac
	+ Linux

Prerequiesites:
	+ python3
	+ pip3

Run
		Run "python3 cs132_twitterfeed.py" in terminal
		Wait for the line "[OK] Server is listening to http://localhost:8082/feed/start"
    Run "python -m SimpleHTTPServer 8080 (or any other port number)"
    Then open a browser and go to "http://localhost:8080/index.html"

Stop:
	CTRL-C to stop the server

Troubleshotting:
	if the server cannot start because "address is in use", wait some time and start the server again, or change another port number.

Acknowledgement:
  This project is based upon Zhengyi Peng's swiftfeed server (https://github.com/pengzhengyi/swiftfeed)
  
