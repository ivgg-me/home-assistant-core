"""Constants for the Tuya integration."""
from dataclasses import dataclass
from enum import Enum

from tuya_iot import TuyaCloudOpenAPIEndpoint

DOMAIN = "tuya"

CONF_AUTH_TYPE = "auth_type"
CONF_PROJECT_TYPE = "tuya_project_type"
CONF_ENDPOINT = "endpoint"
CONF_ACCESS_ID = "access_id"
CONF_ACCESS_SECRET = "access_secret"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_COUNTRY_CODE = "country_code"
CONF_APP_TYPE = "tuya_app_type"

TUYA_DISCOVERY_NEW = "tuya_discovery_new"
TUYA_HA_SIGNAL_UPDATE_ENTITY = "tuya_entry_update"

TUYA_RESPONSE_CODE = "code"
TUYA_RESPONSE_RESULT = "result"
TUYA_RESPONSE_MSG = "msg"
TUYA_RESPONSE_SUCCESS = "success"
TUYA_RESPONSE_PLATFORM_URL = "platform_url"

TUYA_SUPPORTED_PRODUCT_CATEGORIES = (
    "bh",  # Smart Kettle
    "cwysj",  # Pet Water Feeder
    "cz",  # Socket
    "dc",  # Light string
    "dd",  # Light strip
    "dj",  # Light
    "dlq",  # Breaker
    "fs",  # Fan
    "fs",  # Fan
    "fwl",  # Ambient light
    "kfj",  # Coffee maker
    "kg",  # Switch
    "kj",  # Air Purifier
    "kt",  # Air conditioner
    "ldcg",  # Luminance Sensor
    "mcs",  # Door Window Sensor
    "pc",  # Power Strip
    "pir",  # PIR Detector
    "qn",  # Heater
    "sgbj",  # Siren Alarm
    "sos",  # SOS Button
    "sp",  # Smart Camera
    "wk",  # Thermostat
    "xdd",  # Ceiling Light
    "xxj",  # Diffuser
)

TUYA_SMART_APP = "tuyaSmart"
SMARTLIFE_APP = "smartlife"

PLATFORMS = [
    "binary_sensor",
    "camera",
    "climate",
    "fan",
    "light",
    "number",
    "scene",
    "select",
    "sensor",
    "siren",
    "switch",
]


class DPCode(str, Enum):
    """Device Property Codes used by Tuya.

    https://developer.tuya.com/en/docs/iot/standarddescription?id=K9i5ql6waswzq
    """

    ALARM_SWITCH = "alarm_switch"  # Alarm switch
    ALARM_TIME = "alarm_time"  # Alarm time
    ALARM_VOLUME = "alarm_volume"  # Alarm volume
    ANION = "anion"  # Ionizer unit
    BATTERY_PERCENTAGE = "battery_percentage"  # Battery percentage
    BATTERY_STATE = "battery_state"  # Battery state
    BRIGHT_STATE = "bright_state"  # Brightness status
    BRIGHT_VALUE = "bright_value"  # Brightness
    C_F = "c_f"  # Temperature unit switching
    CHILD_LOCK = "child_lock"  # Child lock
    CO2_VALUE = "co2_value"  # CO2 concentration
    COLOUR_DATA = "colour_data"  # Colored light mode
    COLOUR_DATA_V2 = "colour_data_v2"  # Colored light mode
    CONCENTRATION_SET = "concentration_set"  # Concentration setting
    CUP_NUMBER = "cup_number"  # NUmber of cups
    CUR_CURRENT = "cur_current"  # Actual current
    CUR_POWER = "cur_power"  # Actual power
    CUR_VOLTAGE = "cur_voltage"  # Actual voltage
    DOORCONTACT_STATE = "doorcontact_state"  # Status of door window sensor
    FAN_DIRECTION = "fan_direction"  # Fan direction
    FAN_SPEED_ENUM = "fan_speed_enum"  # Speed mode
    FAN_SPEED_PERCENT = "fan_speed_percent"  # Stepless speed
    FILTER_RESET = "filter_reset"  # Filter (cartridge) reset
    HUMIDITY_CURRENT = "humidity_current"  # Current humidity
    HUMIDITY_SET = "humidity_set"  # Humidity setting
    HUMIDITY_VALUE = "humidity_value"  # Humidity
    LIGHT = "light"  # Light
    LOCK = "lock"  # Lock / Child lock
    MATERIAL = "material"  # Material
    MODE = "mode"  # Working mode / Mode
    MOTION_SWITCH = "motion_switch"  # Motion switch
    MUFFLING = "muffling"  # Muffling
    PIR = "pir"  # Motion sensor
    POWDER_SET = "powder_set"  # Powder
    PUMP_RESET = "pump_reset"  # Water pump reset
    RECORD_SWITCH = "record_switch"  # Recording switch
    SHAKE = "shake"  # Oscillating
    SOS = "sos"  # Emergency State
    SOS_STATE = "sos_state"  # Emergency mode
    SPEED = "speed"  # Speed level
    START = "start"  # Start
    SWING = "swing"  # Swing mode
    SWITCH = "switch"  # Switch
    SWITCH_1 = "switch_1"  # Switch 1
    SWITCH_2 = "switch_2"  # Switch 2
    SWITCH_3 = "switch_3"  # Switch 3
    SWITCH_4 = "switch_4"  # Switch 4
    SWITCH_5 = "switch_5"  # Switch 5
    SWITCH_6 = "switch_6"  # Switch 6
    SWITCH_BACKLIGHT = "switch_backlight"  # Backlight switch
    SWITCH_HORIZONTAL = "switch_horizontal"  # Horizontal swing flap switch
    SWITCH_LED = "switch_led"  # Switch
    SWITCH_SPRAY = "switch_spray"  # Spraying switch
    SWITCH_USB1 = "switch_usb1"  # USB 1
    SWITCH_USB2 = "switch_usb2"  # USB 2
    SWITCH_USB3 = "switch_usb3"  # USB 3
    SWITCH_USB4 = "switch_usb4"  # USB 4
    SWITCH_USB5 = "switch_usb5"  # USB 5
    SWITCH_USB6 = "switch_usb6"  # USB 6
    SWITCH_VERTICAL = "switch_vertical"  # Vertical swing flap switch
    SWITCH_VOICE = "switch_voice"  # Voice switch
    TEMP_CURRENT = "temp_current"  # Current temperature in °C
    TEMP_CURRENT_F = "temp_current_f"  # Current temperature in °F
    TEMP_SET = "temp_set"  # Set the temperature in °C
    TEMP_SET_F = "temp_set_f"  # Set the temperature in °F
    TEMP_UNIT_CONVERT = "temp_unit_convert"  # Temperature unit switching
    TEMP_VALUE = "temp_value"  # Color temperature
    TEMPER_ALARM = "temper_alarm"  # Tamper alarm
    UV = "uv"  # UV sterilization
    WARM = "warm"  # Heat preservation
    WARM_TIME = "warm_time"  # Heat preservation time
    WATER_RESET = "water_reset"  # Resetting of water usage days
    WATER_SET = "water_set"  # Water level
    WET = "wet"  # Humidification
    WORK_MODE = "work_mode"  # Working mode


@dataclass
class Country:
    """Describe a supported country."""

    name: str
    country_code: str
    endpoint: str = TuyaCloudOpenAPIEndpoint.AMERICA


# https://developer.tuya.com/en/docs/iot/oem-app-data-center-distributed?id=Kafi0ku9l07qb#title-4-China%20Data%20Center
TUYA_COUNTRIES = [
    Country("Afghanistan", "93"),
    Country("Albania", "355"),
    Country("Algeria", "213"),
    Country("American Samoa", "1-684"),
    Country("Andorra", "376"),
    Country("Angola", "244"),
    Country("Anguilla", "1-264"),
    Country("Antarctica", "672"),
    Country("Antigua and Barbuda", "1-268"),
    Country("Argentina", "54", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Armenia", "374"),
    Country("Aruba", "297"),
    Country("Australia", "61"),
    Country("Austria", "43", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Azerbaijan", "994"),
    Country("Bahamas", "1-242"),
    Country("Bahrain", "973"),
    Country("Bangladesh", "880"),
    Country("Barbados", "1-246"),
    Country("Belarus", "375"),
    Country("Belgium", "32", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Belize", "501"),
    Country("Benin", "229"),
    Country("Bermuda", "1-441"),
    Country("Bhutan", "975"),
    Country("Bolivia", "591"),
    Country("Bosnia and Herzegovina", "387"),
    Country("Botswana", "267"),
    Country("Brazil", "55", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("British Indian Ocean Territory", "246"),
    Country("British Virgin Islands", "1-284"),
    Country("Brunei", "673"),
    Country("Bulgaria", "359"),
    Country("Burkina Faso", "226"),
    Country("Burundi", "257"),
    Country("Cambodia", "855"),
    Country("Cameroon", "237"),
    Country("Canada", "1", TuyaCloudOpenAPIEndpoint.AMERICA),
    Country("Cape Verde", "238"),
    Country("Cayman Islands", "1-345"),
    Country("Central African Republic", "236"),
    Country("Chad", "235"),
    Country("Chile", "56"),
    Country("China", "86", TuyaCloudOpenAPIEndpoint.CHINA),
    Country("Christmas Island", "61"),
    Country("Cocos Islands", "61"),
    Country("Colombia", "57"),
    Country("Comoros", "269"),
    Country("Cook Islands", "682"),
    Country("Costa Rica", "506"),
    Country("Croatia", "385", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Cuba", "53"),
    Country("Curacao", "599"),
    Country("Cyprus", "357", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Czech Republic", "420", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Democratic Republic of the Congo", "243"),
    Country("Denmark", "45", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Djibouti", "253"),
    Country("Dominica", "1-767"),
    Country("Dominican Republic", "1-809"),
    Country("East Timor", "670"),
    Country("Ecuador", "593"),
    Country("Egypt", "20"),
    Country("El Salvador", "503"),
    Country("Equatorial Guinea", "240"),
    Country("Eritrea", "291"),
    Country("Estonia", "372", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Ethiopia", "251"),
    Country("Falkland Islands", "500"),
    Country("Faroe Islands", "298"),
    Country("Fiji", "679"),
    Country("Finland", "358", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("France", "33", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("French Polynesia", "689"),
    Country("Gabon", "241"),
    Country("Gambia", "220"),
    Country("Georgia", "995"),
    Country("Germany", "49", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Ghana", "233"),
    Country("Gibraltar", "350"),
    Country("Greece", "30", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Greenland", "299"),
    Country("Grenada", "1-473"),
    Country("Guam", "1-671"),
    Country("Guatemala", "502"),
    Country("Guernsey", "44-1481"),
    Country("Guinea", "224"),
    Country("Guinea-Bissau", "245"),
    Country("Guyana", "592"),
    Country("Haiti", "509"),
    Country("Honduras", "504"),
    Country("Hong Kong", "852"),
    Country("Hungary", "36", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Iceland", "354", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("India", "91", TuyaCloudOpenAPIEndpoint.INDIA),
    Country("Indonesia", "62"),
    Country("Iran", "98"),
    Country("Iraq", "964"),
    Country("Ireland", "353", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Isle of Man", "44-1624"),
    Country("Israel", "972"),
    Country("Italy", "39", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Ivory Coast", "225"),
    Country("Jamaica", "1-876"),
    Country("Japan", "81", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Jersey", "44-1534"),
    Country("Jordan", "962"),
    Country("Kazakhstan", "7"),
    Country("Kenya", "254"),
    Country("Kiribati", "686"),
    Country("Kosovo", "383"),
    Country("Kuwait", "965"),
    Country("Kyrgyzstan", "996"),
    Country("Laos", "856"),
    Country("Latvia", "371", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Lebanon", "961"),
    Country("Lesotho", "266"),
    Country("Liberia", "231"),
    Country("Libya", "218"),
    Country("Liechtenstein", "423", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Lithuania", "370", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Luxembourg", "352", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Macau", "853"),
    Country("Macedonia", "389"),
    Country("Madagascar", "261"),
    Country("Malawi", "265"),
    Country("Malaysia", "60"),
    Country("Maldives", "960"),
    Country("Mali", "223"),
    Country("Malta", "356", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Marshall Islands", "692"),
    Country("Mauritania", "222"),
    Country("Mauritius", "230"),
    Country("Mayotte", "262"),
    Country("Mexico", "52"),
    Country("Micronesia", "691"),
    Country("Moldova", "373"),
    Country("Monaco", "377"),
    Country("Mongolia", "976"),
    Country("Montenegro", "382"),
    Country("Montserrat", "1-664"),
    Country("Morocco", "212"),
    Country("Mozambique", "258"),
    Country("Myanmar", "95"),
    Country("Namibia", "264"),
    Country("Nauru", "674"),
    Country("Nepal", "977"),
    Country("Netherlands", "31", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Netherlands Antilles", "599"),
    Country("New Caledonia", "687"),
    Country("New Zealand", "64"),
    Country("Nicaragua", "505"),
    Country("Niger", "227"),
    Country("Nigeria", "234"),
    Country("Niue", "683"),
    Country("North Korea", "850"),
    Country("Northern Mariana Islands", "1-670"),
    Country("Norway", "47"),
    Country("Oman", "968"),
    Country("Pakistan", "92"),
    Country("Palau", "680"),
    Country("Palestine", "970"),
    Country("Panama", "507"),
    Country("Papua New Guinea", "675"),
    Country("Paraguay", "595"),
    Country("Peru", "51"),
    Country("Philippines", "63"),
    Country("Pitcairn", "64"),
    Country("Poland", "48", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Portugal", "351", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Puerto Rico", "1-787, 1-939"),
    Country("Qatar", "974"),
    Country("Republic of the Congo", "242"),
    Country("Reunion", "262"),
    Country("Romania", "40", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Russia", "7", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Rwanda", "250"),
    Country("Saint Barthelemy", "590"),
    Country("Saint Helena", "290"),
    Country("Saint Kitts and Nevis", "1-869"),
    Country("Saint Lucia", "1-758"),
    Country("Saint Martin", "590"),
    Country("Saint Pierre and Miquelon", "508"),
    Country("Saint Vincent and the Grenadines", "1-784"),
    Country("Samoa", "685"),
    Country("San Marino", "378"),
    Country("Sao Tome and Principe", "239"),
    Country("Saudi Arabia", "966"),
    Country("Senegal", "221"),
    Country("Serbia", "381"),
    Country("Seychelles", "248"),
    Country("Sierra Leone", "232"),
    Country("Singapore", "65"),
    Country("Sint Maarten", "1-721"),
    Country("Slovakia", "421", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Slovenia", "386", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Solomon Islands", "677"),
    Country("Somalia", "252"),
    Country("South Africa", "27"),
    Country("South Korea", "82"),
    Country("South Sudan", "211"),
    Country("Spain", "34", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Sri Lanka", "94"),
    Country("Sudan", "249"),
    Country("Suriname", "597"),
    Country("Svalbard and Jan Mayen", "47", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Swaziland", "268"),
    Country("Sweden", "46", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("Switzerland", "41"),
    Country("Syria", "963"),
    Country("Taiwan", "886"),
    Country("Tajikistan", "992"),
    Country("Tanzania", "255"),
    Country("Thailand", "66"),
    Country("Togo", "228"),
    Country("Tokelau", "690"),
    Country("Tonga", "676"),
    Country("Trinidad and Tobago", "1-868"),
    Country("Tunisia", "216"),
    Country("Turkey", "90"),
    Country("Turkmenistan", "993"),
    Country("Turks and Caicos Islands", "1-649"),
    Country("Tuvalu", "688"),
    Country("U.S. Virgin Islands", "1-340"),
    Country("Uganda", "256"),
    Country("Ukraine", "380"),
    Country("United Arab Emirates", "971"),
    Country("United Kingdom", "44", TuyaCloudOpenAPIEndpoint.EUROPE),
    Country("United States", "1", TuyaCloudOpenAPIEndpoint.AMERICA),
    Country("Uruguay", "598"),
    Country("Uzbekistan", "998"),
    Country("Vanuatu", "678"),
    Country("Vatican", "379"),
    Country("Venezuela", "58"),
    Country("Vietnam", "84"),
    Country("Wallis and Futuna", "681"),
    Country("Western Sahara", "212"),
    Country("Yemen", "967"),
    Country("Zambia", "260"),
    Country("Zimbabwe", "263"),
]
