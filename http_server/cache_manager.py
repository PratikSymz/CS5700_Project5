import csv, os


CACHE_LIMIT = 20000000

class Cache_Manager:

    ''' Initiate some SHIT '''
    def __init__(self):
        self.available_cache = CACHE_LIMIT

        # Dictionary of Popularity keyword and its number of hits
        self.popularity_rate_mapping = {}

    def load_popularity_data(self):
        ''' Load popularity rates and the corresponding search query from the CSV file '''
        ''' Params: none, Returns: none '''

        # Open CSV file
        try:
            csv_file = open('pageviews_modded.csv', 'r')
        except:
            print('Unable to open Popularity Rate CSV file (pageviews_modded.csv)...')
            return False

        # Parse CSV file
        try:
            csv_reader = csv.reader(csv_file)
            # Read line items
            for line_item in csv_reader:
                # Map popularity keyword to the its number of hits
                self.popularity_rate_mapping[str(line_item[0])] = int(line_item[1])

            # Close file
            csv_file.close()

        except:
            print('Unable to read data from CSV file...')
            return False

        return True

    def mobilize_server_cache(self, path: str):
        ''' Setup caching when server is started. Takes in path to the cache as param to setup cache there. '''
        # The CACHE does not exist in the current path
        # Create a new CACHE dir and return to the main program
        if (not os.path.exists(path)):
            try:
                directory = os.path.join(path, 'wiki')
                # Create the Wiki CACHE dir
                os.mkdir(directory)
                return True
        
            except OSError as os_error:
                print('Unable to create Cache Directory...', os_error)
                return False

        # The CACHE exists in the current path
        # Read all the subdirectories for all the webpages
        for dir in os.listdir(path):
            dir_name = os.path.join(path, dir)

            # If dir is a directory
            if (os.path.isdir(dir_name)):
                # Read this directory further and extract all the sub-dr files
                self.mobilize_server_cache(dir_name)

            # If dir is a file
            if (os.path.isfile(dir_name)):
                # Retrieve the file size
                dir_size = os.path.getsize(dir_name)
                # If the file size is greater than the cache size limit, evict the directory
                if (dir_size > self.available_cache):
                    os.remove(dir_name)

                # Reduce the available space
                else:
                    self.available_cache -= dir_size