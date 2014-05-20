import datetime
from django.db import models
from django.contrib.auth.models import User


class UserProfile (models.Model):
    '''Extends the information attached to ESPA users with a one-to-one
    relationship. The other options were to extend the actual Django User
    model or create an entirely new User model.  This is the cleanest and
    recommended method per the Django docs.
    '''
    # reference to the User this Profile belongs to
    user = models.OneToOneField(User)

    # The EE contactid of this user
    contactid = models.CharField(max_length=10)


class Order(models.Model):
    '''Persistent object that models a user order for processing.'''

    def __unicode__(self):
        return self.orderid

    ORDER_TYPES = (
        ('level2_ondemand', 'Level 2 On Demand'),
        ('lpvs', 'Product Validation')
    )

    STATUS = (
        ('ordered', 'Ordered'),
        ('partial', 'Partially Filled'),
        ('complete', 'Complete')
    )

    ORDER_SOURCE = (
        ('espa', 'ESPA'),
        ('ee', 'EE')
    )

    # orderid should be in the format email_MMDDYY_HHMMSS
    orderid = models.CharField(max_length=255, unique=True, db_index=True)

    # This field is in the User object now, but should actually be pulled from
    # the EarthExplorer profile
    # the users email address
    email = models.EmailField(db_index=True)

    # reference the user that placed this order
    user = models.ForeignKey(User)

    # order_type describes the order characteristics so we can use logic to
    # handle multiple varieties of orders
    order_type = models.CharField(max_length=50,
                                  choices=ORDER_TYPES,
                                  db_index=True)

    # date the order was placed
    order_date = models.DateTimeField('date ordered',
                                      blank=True,
                                      db_index=True)

    # date the order completed (all scenes completed or marked unavailable)
    completion_date = models.DateTimeField('date completed',
                                           blank=True,
                                           null=True,
                                           db_index=True)

    #o ne of order.STATUS
    status = models.CharField(max_length=20, choices=STATUS, db_index=True)

    # space for users to add notes to orders
    note = models.CharField(max_length=2048, blank=True, null=True)

    # json for all product options
    product_options = models.TextField(blank=False, null=False)

    # one of Order.ORDER_SOURCE
    order_source = models.CharField(max_length=10,
                                    choices=ORDER_SOURCE,
                                    db_index=True)

    # populated when the order is placed through EE vs ESPA
    ee_order_id = models.CharField(max_length=13, blank=True)

    def get_default_product_options(self):
        '''Factory method to return default product selection options

        Return:
        Dictionary populated with default product options
        '''
        o = {}
        # standard product selection options
        o['include_sourcefile'] = False       # underlying raster
        o['include_source_metadata'] = False  # source metadata
        o['include_sr_toa'] = False           # LEDAPS top of atmosphere
        o['include_sr_thermal'] = False       # LEDAPS band 6
        o['include_sr'] = False               # LEDAPS surface reflectance
        o['include_sr_browse'] = False        # surface reflectance browse
        o['include_sr_ndvi'] = False          # normalized difference veg
        o['include_sr_ndmi'] = False          # normalized difference moisture
        o['include_sr_nbr'] = False           # normalized burn ratio
        o['include_sr_nbr2'] = False          # normalized burn ratio 2
        o['include_sr_savi'] = False          # soil adjusted vegetation
        o['include_sr_msavi'] = False         # modified soil adjusted veg
        o['include_sr_evi'] = False           # enhanced vegetation
        o['include_swe'] = False              # surface water extent
        o['include_sca'] = False              # snow covered area
        o['include_solr_index'] = False       # solr search index record
        o['include_cfmask'] = False           # (deprecated)

        return o

    def get_default_projection_options(self):
        '''Factory method to return default reprojection options

        Return:
        Dictionary populated with default reprojection options
        '''
        o = {}
        o['reproject'] = False             # reproject all rasters (True/False)
        o['target_projection'] = None      # if 'reproject' which projection?
        o['central_meridian'] = None       #
        o['false_easting'] = None          #
        o['false_northing'] = None         #
        o['origin_lat'] = None             #
        o['std_parallel_1'] = None         #
        o['std_parallel_2'] = None         #
        o['datum'] = 'wgs84'               #

        #utm only options
        o['utm_zone'] = None               # 1 to 60
        o['utm_north_south'] = None        # north or south

        return o

    def get_default_subset_options(self):
        '''Factory method to return default subsetting/framing options

        Return:
        Dictionary populated with default subsettings/framing options
        '''
        o = {}
        o['image_extents'] = False     # modify image extents (subset or frame)
        o['minx'] = None               #
        o['miny'] = None               #
        o['maxx'] = None               #
        o['maxy'] = None               #
        return o

    def get_default_resize_options(self):
        '''Factory method to return default resizing options

        Return:
        Dictionary populated with default resizing options
        '''
        o = {}
        #Pixel resizing options
        o['resize'] = False            # resize output pixel size (True/False)
        o['pixel_size'] = None         # if resize, how big (30 to 1000 meters)
        o['pixel_size_units'] = None   # meters or dd.

        return o

    def get_default_resample_options(self):
        '''Factory method to returns default resampling options

        Return:
        Dictionary populated with default resampling options
        '''
        o = {}
        o['resample_method'] = 'near'  # how would user like to resample?

        return o

    def get_default_options(self):
        '''Factory method to return default espa order options

        Return:
        Dictionary populated with default espa ordering options
        '''
        o = {}
        o.update(self.get_default_product_options())
        o.update(self.get_default_projection_options())
        o.update(self.get_default_subset_options())
        o.update(self.get_default_resize_options())
        o.update(self.get_default_resample_options())
        
        return o
        
        
    def get_default_ee_options(self):
        '''Factory method to return default espa order options for orders
        originating in through Earth Explorer
        
        Return:
        Dictionary populated with default espa options for ee
        '''
        o = {}
        o['include_sourcefile'] = False        
        o['include_source_metadata'] = False
        o['include_sr_toa'] =  False
        o['include_sr_thermal'] =  False
        o['include_sr'] = True
        o['include_sr_browse'] = False
        o['include_sr_ndvi'] = False
        o['include_sr_ndmi'] = False
        o['include_sr_nbr'] = False
        o['include_sr_nbr2'] = False
        o['include_sr_savi'] = False
        o['include_sr_evi'] = False
        o['include_solr_index'] = False
        o['include_cfmask'] = False
        o['reproject'] = False
        o['resize'] = False
        o['image_extents'] = False
        
        return o
    

    def generate_order_id(self, email):
        '''Generate espa order id if the order comes from the bulk ordering
        or the api'''
        d = datetime.datetime.now()
        return '%s-%s%s%s-%s%s%s' % (email,
                                     d.month,
                                     d.day,
                                     d.year,
                                     d.hour,
                                     d.minute,
                                     d.second)

    def generate_ee_order_id(self, email, eeorder):
        '''Generate an order id if the order came from Earth Explorer

        Keyword args:
        email -- Email address of the requestor
        eeorder -- The Earth Explorer order id

        Return:
        An order id string for the espa system for ee created orders
        str(email-eeorder)
        '''
        return '%s-%s' % (email, eeorder)


class Scene(models.Model):
    '''Persists a scene object as defined from the ordering and tracking
    perspective'''

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.status)

    #enumeration of valid status flags a scene may have
    STATUS = (
        ('submitted', 'Submitted'),
        ('onorder', 'On Order'),
        ('oncache', 'On Cache'),
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('complete', 'Complete'),
        ('purged', 'Purged'),
        ('unavailable', 'Unavailable'),
        ('error', 'Error')
    )

    #scene file name, with no suffix
    name = models.CharField(max_length=256, db_index=True)

    #scene system note, used to add message to users
    note = models.CharField(max_length=2048, blank=True, null=True)

    #Reference to the Order this Scene is associated with
    order = models.ForeignKey(Order)

    #full path including filename where this scene has been distributed to
    #minus the host and port. signifies that this scene is distributed
    product_distro_location = models.CharField(max_length=1024, blank=True)

    #full path for scene download on the distribution node
    product_dload_url = models.CharField(max_length=1024, blank=True)

    #full path (with filename) for scene checksum on distribution filesystem
    cksum_distro_location = models.CharField(max_length=1024, blank=True)

    #full url this file can be downloaded from
    cksum_download_url = models.CharField(max_length=1024, blank=True)

    # This will only be populated if the scene had to be placed on order
    #through EE to satisfy the request.
    tram_order_id = models.CharField(max_length=13, blank=True, null=True)

    # Flags for order origination.  These will only be populated if the scene
    # request came from EE.
    ee_unit_id = models.IntegerField(max_length=11, blank=True, null=True)

    # General status flags for this scene

    #Status.... one of Submitted, Ready For Processing, Processing,
    #Processing Complete, Distributed, or Purged
    status = models.CharField(max_length=30, choices=STATUS, db_index=True)

    #Where is this scene being processed at?  (which machine)
    processing_location = models.CharField(max_length=256, blank=True)

    #Time this scene was finished processing
    completion_date = models.DateTimeField('date completed',
                                           blank=True,
                                           null=True,
                                           db_index=True)

    #Final contents of log file... should be put added when scene is marked
    #complete.
    log_file_contents = models.TextField('log_file', blank=True, null=True)


class Configuration(models.Model):
    '''Implements a key/value datastore on top of a relational database
    '''
    key = models.CharField(max_length=255, unique=True)
    value = models.CharField(max_length=2048)

    def __unicode__(self):
        return ('%s : %s') % (self.key, self.value)

    def getValue(self, key):

        c = Configuration.objects.filter(key=key)

        if len(c) > 0:
            return str(c[0].value)
        else:
            return ''
