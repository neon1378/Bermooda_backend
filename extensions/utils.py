from . import jalali
from django.utils import timezone
from datetime import datetime


def persian_numbers_converter(mystr):
    numbers = {
        "0": "۰",
        "1": "۱",
        "2": "۲",
        "3": "۳",
        "4": "۴",
        "5": "۵",
        "6": "۶",
        "7": "۷",
        "8": "۸",
        "9": "۹",
    }

    for e, p in numbers.items():
        mystr = mystr.replace(e, p)

    return mystr


def jalali_converter(time):
    jmonth = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "14"]

    time = timezone.localtime(time)

    time_to_str = "{},{},{}".format(time.year, time.month, time.day)
    time_to_tuple = jalali.Gregorian(time_to_str).persian_tuple()

    time_to_list = list(time_to_tuple)

    for index, month in enumerate(jmonth):
        if time_to_list[1] == index + 1:
            time_to_list[1] = month
            break

    output = "{} {} {}، ساعت {}:{}".format(
        time_to_list[0],
        time_to_list[1],
        time_to_list[2],
 
    )
    list_date=output.split(" ")


    q=0
    item=""
    for i in list_date:
       if q == 0:
           item+=f"{i}"
           q+=1
       elif q== 1:
            item+=f"/{i}/"
            q+=1
       else:
           item+=f"{i}/"

   
    
    return persian_numbers_converter(output)


# اضافه شده
def jalali_converter(time):
    jmonth = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]

    time_to_str = "{},{},{}".format(time.year, time.month, time.day)
    time_to_tuple = jalali.Gregorian(time_to_str).persian_tuple()

    time_to_list = list(time_to_tuple)

    for index, month in enumerate(jmonth):
        if time_to_list[1] == index + 1:
            time_to_list[1] = month
            break

    output = "{} {} {}".format(
        time_to_list[0],
        time_to_list[1],
        time_to_list[2],


    )
    list_date=output.split(" ")
  
    q=0
    item=""
    for i in list_date:
       if q == 0:
           item+=f"{i}/"
           q+=1
       elif q== 1:
            item+=f"{i}/"
            q+=1
       else:
           item+=i
  

    return persian_numbers_converter(item)
def jalali_converter_only_date(time):
    jmonth = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]

    time_to_str = "{},{},{}".format(time.year, time.month, time.day)
    time_to_tuple = jalali.Gregorian(time_to_str).persian_tuple()

    time_to_list = list(time_to_tuple)

  
    
    for index, month in enumerate(jmonth):
        if time_to_list[1] == index + 1:
            time_to_list[1] = month
            break
    output = "{} {} {}".format(
        time_to_list[0],
        time_to_list[1],
        time_to_list[2],


    )
    list_date=output.split(" ")
  
    q=0
    item=""
    for i in list_date:
       if q == 0:
           item+=f"{i}/"
           q+=1
       elif q== 1:
            item+=f"{i}/"
            q+=1
       else:
           item+=i
  

    return persian_numbers_converter(item)

def costum_date(time):
    jmonth = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]

    time_to_str = "{},{},{}".format(time.year, time.month, time.day)
    time_to_tuple = jalali.Gregorian(time_to_str).persian_tuple()

    time_to_list = list(time_to_tuple)



    for index, month in enumerate(jmonth):
        if time_to_list[1] == index + 1:
            time_to_list[1] = month
            break
    output = "{} {} {}".format(
        time_to_list[0],
        time_to_list[1],
        time_to_list[2],


    )
    list_date=output.split(" ")
  
    q=0
    item=""
    for i in list_date:
       if q == 0:
           item+=f"{i}/"
           q+=1
       elif q== 1:
            item+=f"{i}/"
            q+=1
       else:
           item+=i
  

    return item




# اضافه شده
def date_gregorain_converter(date):
    time_to_tuple = jalali.Persian(date).gregorian_tuple()
    x = str(time_to_tuple)
    time_to_str = x.replace(",", "-").replace(")", "").replace("(", "").replace(" ", "")
    # start_day_new = datetime.strptime(start_day, '%Y/%m/%d').strftime('%Y-%m-%d')
    return time_to_str


def jalali_converter_only_date_peson(time):
    jmonth = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]

    time_to_str = "{},{},{}".format(time.year, time.month, time.day)
    time_to_tuple = jalali.Gregorian(time_to_str).persian_tuple()

    time_to_list = list(time_to_tuple)
    
    for index, month in enumerate(jmonth):
        if time_to_list[1] == index + 1:
            time_to_list[1] = month
            break

    output = "{} {} {}".format(
        f"{time_to_list[2]}",
        f"{time_to_list[1]}",
        f"{time_to_list[0]}",


    )

    



    return output