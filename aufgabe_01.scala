object aufgabe_01 {
    abstract class Datum() {
        def print_date(): Unit = {
        
        }
        def print_date_short(): Unit = {
        
        }
    }
    class DatumUS(var day: Int, var month: Int, var year: Int) extends Datum {
        val months = Map(1->"January",2->"February",3->"March",4->"April",5->"May",6->"June",
                7->"July",8->"August",9->"September",10->"October",11->"November",12->"December")
        override def print_date(): Unit = {
            println(s"${months(month)} $day $year")
        }
        override def print_date_short(): Unit = {
            var year_str: String = year.toString()
            var year_short: String = year_str.substring(year_str.length - 2)
            println(s"$month/$day/$year_short")
        }
    }
    class DatumDE(var day: Int, var month: Int, var year: Int) extends Datum {
        val months = Map(1->"Januar",2->"Februar",3->"März",4->"April",5->"Mai",6->"Juni",
                7->"Juli",8->"August",9->"September",10->"Oktober",11->"November",12->"Dezember")
        override def print_date(): Unit = {
            println(s"$day. ${months(month)} $year")
        }
        override def print_date_short(): Unit = {
            var year_str: String = year.toString()
            var year_short: String = year_str.substring(year_str.length - 2)
            println(s"$day.$month.$year_short")
        }
    }
    def main(args: Array[String]): Unit = {
        var date_01: DatumDE = DatumDE(3,12,2003)
        var date_02: DatumUS = DatumUS(3,12,2003)
        date_01.print_date()
        date_01.print_date_short()
        date_02.print_date()
        date_02.print_date_short()
    }
}