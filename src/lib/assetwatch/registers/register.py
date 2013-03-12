class Register():

    def recognized_extensions(self):
        return ()

    def new_file_detected(self, file):
        pass

    def file_deleted(self, file):
        pass

    def file_modified(self, file):
        pass
