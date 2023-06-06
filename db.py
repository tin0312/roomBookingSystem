import pymysql
import datetime


class Database:
    def __init__(self):
        host = "localhost"
        user = "root"
        pwd = "100709100tT."
        db = "mysql"

        self.con = pymysql.connect(
            host=host, user=user, password=pwd, db=db, cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.con.cursor()

    def make_reservation(self, roomNo, startTime, endTime, date, occupancy, username):
        try:
            self.cur.execute(
                "SELECT * FROM room WHERE roomNo = %s", roomNo)
            room = self.cur.fetchone()

            if not room:
                return False, "Room does not exist"

            available, msg = isAvailable(
                date, startTime, endTime, room['maxReservationDuration'])

            if not available:
                return False, msg
            self.cur.execute("INSERT INTO reservation (roomNo, start_time, end_time, date, occupancy, username) VALUES (%s, %s, %s, %s, %s, %s)", (
                roomNo, startTime.strftime('%H:%M:%S'), endTime.strftime('%H:%M:%S'), date.strftime('%Y-%m-%d'), occupancy, username))
            reservation_id = self.cur.lastrowid
            self.con.commit()
            self.cur.execute(
                "SELECT * FROM reservation WHERE reservation_id = %s", reservation_id)
            data = self.cur.fetchall()
            return True, data
        except Exception as e:
            print(e)
            self.con.rollback()
            return False, "Failed to make reservation"

    def get_reservations(self, username):
        try:
            self.cur.execute(
                "SELECT * FROM reservation WHERE username = %s order by date desc", username)
            data = self.cur.fetchall()
            return True, data
        except Exception as e:
            print(e)
            return False, "Failed to get reservations"

    def get_all_reservations(self):
        try:
            self.cur.execute(
                "SELECT * FROM reservation order by date desc")
            data = self.cur.fetchall()
            return True, data
        except Exception as e:
            print(e)
            return False, "Failed to get reservations"

    def get_reservation(self, reservation_id):
        try:
            self.cur.execute(
                "SELECT * FROM reservation WHERE reservation_id = %s", reservation_id)
            data = self.cur.fetchone()
            if data is None:
                return False, "Reservation does not exist"
            return True, data
        except Exception as e:
            print(e)
            return False, "Failed to get reservation"

    def cancel_reservation(self, reservation_id, username):
        try:
            succes, reservation = self.get_reservation(reservation_id)

            if not succes and reservation is None:
                return False, "Reservation does not exist"
            else:
                if reservation['username'] != username:
                    return False, "You do not have permission to cancel this reservation"

                if reservation['status'] == 'cancelled':
                    return False, f"Reservation for room {reservation['roomNo']} is already cancelled"

                self.cur.execute(
                    "UPDATE reservation SET status = 'cancelled' WHERE reservation_id = %s", reservation_id
                )
                self.con.commit()
                return True, None

        except Exception as e:
            print(e)
            self.con.rollback()
            return False, "Failed to cancel reservation"
# admin cancel reservation

    def admin_cancel_reservation(self, reservation_id):
        try:
            succes, reservation = self.get_reservation(reservation_id)

            if not succes and reservation is None:
                return False, "Reservation does not exist"
            else:
                if reservation['status'] == 'cancelled':
                    return False, f"Reservation for room {reservation['roomNo']} is already cancelled"

                self.cur.execute(
                    "UPDATE reservation SET status = 'cancelled' WHERE reservation_id = %s", reservation_id
                )
                self.con.commit()
                return True, None

        except Exception as e:
            print(e)
            self.con.rollback()
            return False, "Failed to cancel reservation"

    def modify_reservation(self, reservation_id, roomNo, startTime, endTime, date, occupancy, username):
        try:
            succes, reservation = self.get_reservation(reservation_id)

            if not succes and reservation is None:
                return False, "Reservation does not exist"
            else:
                if reservation['username'] != username:
                    return False, "You do not have permission to modify this reservation"

                if reservation['status'] == 'cancelled':
                    return False, f"Reservation for room {reservation['roomNo']} is already cancelled"

                self.cur.execute(
                    "SELECT * FROM room WHERE roomNo = %s", roomNo)
                rooms = self.cur.fetchall()

                available, msg = isAvailable(
                    date, startTime, endTime, rooms[0]['maxReservationDuration'])

                if not available:
                    return False, msg

                self.cur.execute(
                    "UPDATE reservation SET roomNo = %s, start_time = %s, end_time = %s, date = %s, occupancy = %s WHERE reservation_id = %s", (
                        roomNo, startTime.strftime('%H:%M:%S'), endTime.strftime('%H:%M:%S'), date.strftime('%Y-%m-%d'), occupancy, reservation_id)
                )
                self.con.commit()
                return True, None

        except Exception as e:
            print(e)
            self.con.rollback()
            return False, "Failed to modify reservation"
# admin modify reservation

    def admin_modify_reservation(self, reservation_id, roomNo, startTime, endTime, date, occupancy, username):
        try:
            succes, reservation = self.get_reservation(reservation_id)

            if not succes and reservation is None:
                return False, "Reservation does not exist"
            else:
                if reservation['status'] == 'cancelled':
                    return False, f"Reservation for room {reservation['roomNo']} is already cancelled"

                self.cur.execute(
                    "SELECT * FROM room WHERE roomNo = %s", roomNo)
                rooms = self.cur.fetchall()

                available, msg = isAvailable(
                    date, startTime, endTime, rooms[0]['maxReservationDuration'])

                if not available:
                    return False, msg

                self.cur.execute(
                    "UPDATE reservation SET roomNo = %s, start_time = %s, end_time = %s, date = %s, occupancy = %s WHERE reservation_id = %s", (
                        roomNo, startTime.strftime('%H:%M:%S'), endTime.strftime('%H:%M:%S'), date.strftime('%Y-%m-%d'), occupancy, reservation_id)
                )
                self.con.commit()
                return True, None

        except Exception as e:
            print(e)
            self.con.rollback()
            return False, "Failed to modify reservation"

    def get_all_users(self):
        try:
            self.cur.execute("SELECT * FROM useraccount")
            data = self.cur.fetchall()
            return True, data
        except Exception as e:
            print(e)
            return False, "Failed to get all users"

    def get_all_rooms(self):
        try:
            self.cur.execute(
                "SELECT r.roomNo, r.roomType, t.name FROM room r join roomtype t on r.roomType = t.roomType")
            data = self.cur.fetchall()
            return True, data
        except Exception as e:
            print(e)
            return False, "Failed to get all rooms"


def isAvailable(date, startTime, endTime, maxReservationDuration):
    start = datetime.datetime.combine(date, startTime)
    end = datetime.datetime.combine(date, endTime)
    now = datetime.datetime.now()

    duration = (end - start).seconds / 3600

    if (end - start).seconds / 60 < 15:
        return False, "Reservations must be at least 15 minutes long"

    # duration must be less than max duration allowed
    if duration > maxReservationDuration:
        return False, "Exceeded max duration allowed"

    if (now - start).seconds / 60 < 30:
        return False, "Reservations must be made at least 30 minutes in advance"

    return True, None
