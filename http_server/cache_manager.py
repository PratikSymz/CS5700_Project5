import csv, os


CACHE_LIMIT = 20000000

class Cache_Manager:

    ''' Initiate some SHIT '''
    def __init__(self):
        self.available_cache = CACHE_LIMIT

        # dict{}: Key [Search query/Cache path], Value [Popularity hits]
        self.cache_popularity_mapping = {}
        # dict{}: Key[Search query/Cache path], Value [Size of the file (search query HTML)]
        self.cache_size_mapping = {}
        # dict{}: Key[Search query/Cache path], Value [(Popularity, Size)]
        self.cache_popul_size_mapping = {}

        # Directory name of the Wiki cache
        self.cache_directory = os.path.join(os.getcwd(), 'cache_wiki')

        self.load_popularity_data()
        self.setup_cache(self.cache_directory)

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
                '''
                # TODO
                Re: CSV file Format, there are two escape mechanisms you need to be aware of:
                    If a field contains a , character, the whole field is escaped between a pair of " characters.
                    If a "-escaped field internally contains a "character, the internal" character is expanded to "".
                '''
                # Map search query keyword to the its popularity number
                self.cache_popularity_mapping[str(line_item[0])] = int(line_item[1])

            # Close file
            csv_file.close()
        except:
            print('Unable to read data from CSV file...')
            return False

        return True

    def setup_cache(self, path: str):
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
                self.setup_cache(dir_name)

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

    def update_cache(self, path: str, contents: str):
        ''' Checks if there is space in cache then adds to it. 
        If not, apply an algorithm to decide whether to cache it and evict some other file
        '''
        if (len(contents) <= self.available_cache):
            self.augment_cache(self.cache_directory + path, contents)
        else:
            # Implement the eviction mechanism
            # Set the capacity of the cache and evict based on that
            self.eviction_mechanism(path, contents)

        self.update_cached_data()

    def update_cached_data(self):
        ''' Updated the cached data fields in the cache_popul_size_mapping{} field '''
        for path in self.cache_size_mapping.keys():
            # Extract the name of the file
            wiki_query = path[(path.rfind('/') + 1): ]
            self.cache_popul_size_mapping[path]
        pass
    
    def augment_cache(self, path: str, contents: str):
        ''' Adds a new file in the cache with the contents of the file. '''
        try:
            # Open the file and write the contents
            file = open(path, 'w+')
            file.write(contents)
            file.close()

            # Update the cache size
            self.available_cache -= len(contents)

        except:
            print('Writing to cache failed...')
            return False

        return True

    def read_cache(self, path: str):
        pass
    
    ''' Eviction Mechanism idea: KNAPSACK problem - If we get a file to be put in the cache of a certain size and popularity (value), 
        maximize the value while still being under or equal to the weight limit '''
    def eviction_mechanism(self, path: str, contents: str):
        pass