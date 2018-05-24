from brain.application import create_app

mode = 'aws'
application = create_app(mode=mode)

if __name__ == '__main__':
    application.run()
