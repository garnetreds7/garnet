config = {
    "total_thread": 10,
    "room_url": '532152'
}

room_status = {
    "sd_rmtp_url": None,
    "hd_rmtp_url": None,
    "spd_rmtp_url": None,
    "id": None,
    "name": None,
    "gg_show": None,
    "owner_uid": None,
    "owner_name": None,
    "room_url": None,
    "near_show_time": None,
    "username": None,
    "tags": None,
    "live_stat": None,
    "fans_count": None,
    "weight": None,
    "is_finished": False
}

DOUYU_INDEX = 'http://www.douyu.com/'
ADDR_DANMU_SERVER = 'danmu.douyutv.com'

REGEX_ROOM_INFO = 'var\s\$ROOM\s=\s({.*});'
REGEX_SERVER_INFO = '\$ROOM\.args\s=\s({.*});'
REGEX_USERNAME = '\/username@=(.+)\/nickname'
REGEX_GID = '\/gid@=(\d+)\/'
REGEX_WEIGHT = '\/weight@=(\d+)\/'
REGEX_FANS_COUNT = '\/fans_count@=(\d+)\/'

PORT_DANMU_SERVER = [8602, 8601, 12601, 12602]

STATE_OFFLINE = 'live_stat@=0'
STATE_ONLINE = 'live_stat@=1'
