#
# date interface-class
#
class Date:

    monthNameFromInt : dict[int, str] = { }

    def __init__(self, day : int, month : int, year : int):
        self.__day__ : int
        self.__month__ : int 
        self.__year__ : int

        self.Day = day
        self.Month = month
        self.Year = year

    # returns the date as string formatted to DD. of MM YYYY (month spelled out)
    def toString(self) -> str:
        raise TypeError("Date serves only as an interface-class")
    
    # returns the date as string formatted to DD.MM.YYYY (day, month, year)
    def toShortString(self) -> str:
        raise TypeError("Date serves only as an interface-class")
    
    #
    # used '@'-decorators for implementing setters and getters
    # makes class-usage more explicit (know which attributes are safe to use and change)
    # and also catches errors
    #
    
    #
    # day setter and getter
    #
    @property
    def Day(self) -> int:
        return self.__day__
    
    @Day.setter
    def Day(self, value : int) -> None:
        if (value < 1 or value > 31):
            raise AttributeError("day value out of range")
        self.__day__ = value
    #
    # month setter and getter
    #
    @property
    def Month(self) -> int:
        return self.__month__
    
    @Month.setter
    def Month(self, value : int) -> None:
        if (value < 1 or value > 12):
            raise AttributeError("month value out of range")
        self.__month__ = value
    #
    # year setter and getter
    #
    @property
    def Year(self) -> int:
        return self.__year__
    
    @Year.setter
    def Year(self, value : int) -> None:
        if (value < 1):
            raise AttributeError("year value out of range")
        self.__year__ = value
#
# specialization of date-class for US-specific dates
#
class DateUS(Date):

    monthNameFromInt : dict[int, str] = {
        1 : "January",
        2 : "February",
        3 : "March",
        4 : "April",
        5 : "May",
        6 : "June",
        7 : "July",
        8 : "August",
        9 : "September",
        10 : "October",
        11 : "November",
        12 : "December"
    }

    def __init__(self, day : int, month : int, year : int):
        super().__init__(day, month, year)

    # returns the date as string formatted to DD. of MM YYYY (month spelled out)
    def toString(self) -> str:
        return str(self.__day__) + ". of " + DateUS.monthNameFromInt.get(self.__month__) + " " + str(self.__year__)
    
    # returns the date as string formatted to MM.DD.YYYY (day, month, year)
    def toShortString(self) -> str:
        return str(self.__month__) + "." + str(self.__day__) + "." + str(self.__year__)
#
# specialization of date-class for DE-specific dates
#
class DateDE(Date):

    monthNameFromInt : dict[int, str] = {
        1 : "Januar",
        2 : "Februar",
        3 : "März",
        4 : "April",
        5 : "Mai",
        6 : "Juni",
        7 : "Juli",
        8 : "August",
        9 : "September",
        10 : "Oktober",
        11 : "November",
        12 : "Dezember"
    }

    def __init__(self, day : int, month : int, year : int):
        super().__init__(day, month, year)

    # returns the date as string formatted to DD. MM YYYY (month spelled out)
    def toString(self) -> str:
        return str(self.__day__) + ". " + DateDE.monthNameFromInt.get(self.__month__) + " " + str(self.__year__)
    
    # returns the date as string formatted to DD.MM.YYYY (day, month, year)
    def toShortString(self) -> str:
        return str(self.__day__) + "." + str(self.__month__) + "." + str(self.__year__)

#   
# method to test all of the functionality
#
def unit_test():
    
    # test class instances
    interface : Date = Date(1,1,1900)
    dateUS : DateUS = DateUS(26,5,2025)
    dateDE : DateDE = DateDE(26,5,2025)
    
    # debug prints 1
    try:
        print(interface.toString())
    except TypeError:
        print("interface toString() raised TypeError")
    print(dateUS.toString())
    print(dateDE.toString())
    
    # setters
    dateUS.Day = 20
    dateDE.Day = 20
    try:
        dateUS.Day = 42
    except AttributeError:
        print("dateUS day setter catched faulty value")
    
    # getters
    print("dateUS day: " + str(dateUS.Day))
    print("dateDE year: " + str(dateDE.Year))
    
    # debug prints 2
    print(dateUS.toShortString())
    print(dateDE.toShortString())

    print("unit-test for 'Date' was successful")