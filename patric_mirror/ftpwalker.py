import ftputil
import loader
from model import initialize

host_ip = "128.173.97.104"
user = 'anonymous'
passwd = ''


def make_ftp_client():
    return ftputil.FTPHost(host_ip, user, passwd)


def get_feature_files():
    host = make_ftp_client()
    host.chdir("patric2/genomes")
    for directory, dirnames, files in host.walk("."):
        for item in files:
            if ".features.tab" in item:
                path = '/'.join((directory, item))
                yield host.open(path, 'rb')


def mirror(database_path):
    initialize(database_path)
    for i, features_file in enumerate(get_feature_files()):
        print "On item %d" % i
        loader.load_features(database_path, features_file)
        features_file.close()

if __name__ == '__main__':
    import sys
    mirror(sys.argv[1])
