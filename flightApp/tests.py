from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from flightApp.models import Flight, Passanger, Reservation
from flightApp.serializers import FlightSerializer, PassangerSerializer, ReservationSerializer
import datetime


class FlightModelTest(TestCase):
    def setUp(self):
        self.flight = Flight.objects.create(
            flightNumber="AA123",
            operatingAirLines="American Airlines",
            departureCity="NYC",
            arrivalCity="LAX",
            dateOfDeparture=datetime.date(2024, 3, 15),
            estimatedTimeOfDeparture=datetime.time(10, 30),
        )

    def test_flight_creation(self):
        self.assertEqual(self.flight.flightNumber, "AA123")
        self.assertEqual(self.flight.operatingAirLines, "American Airlines")
        self.assertEqual(self.flight.departureCity, "NYC")
        self.assertEqual(self.flight.arrivalCity, "LAX")
        self.assertEqual(self.flight.dateOfDeparture, datetime.date(2024, 3, 15))
        self.assertEqual(self.flight.estimatedTimeOfDeparture, datetime.time(10, 30))

    def test_flight_str(self):
        flight = Flight.objects.get(id=self.flight.id)
        self.assertIsNotNone(flight)


class PassangerModelTest(TestCase):
    def setUp(self):
        self.passanger = Passanger.objects.create(
            firstName="John",
            lastName="Doe",
            middleName="Q",
            email="john@example.com",
            phone="555-1234",
        )

    def test_passanger_creation(self):
        self.assertEqual(self.passanger.firstName, "John")
        self.assertEqual(self.passanger.lastName, "Doe")
        self.assertEqual(self.passanger.middleName, "Q")
        self.assertEqual(self.passanger.email, "john@example.com")
        self.assertEqual(self.passanger.phone, "555-1234")


class ReservationModelTest(TestCase):
    def setUp(self):
        self.flight = Flight.objects.create(
            flightNumber="UA456",
            operatingAirLines="United Airlines",
            departureCity="SFO",
            arrivalCity="ORD",
            dateOfDeparture=datetime.date(2024, 4, 20),
            estimatedTimeOfDeparture=datetime.time(14, 0),
        )
        self.passanger = Passanger.objects.create(
            firstName="Jane",
            lastName="Smith",
            middleName="A",
            email="jane@example.com",
            phone="555-5678",
        )
        self.reservation = Reservation.objects.create(
            flight=self.flight,
            passanger=self.passanger,
        )

    def test_reservation_creation(self):
        self.assertEqual(self.reservation.flight, self.flight)
        self.assertEqual(self.reservation.passanger, self.passanger)

    def test_reservation_cascade_delete_flight(self):
        flight_id = self.flight.id
        self.flight.delete()
        self.assertFalse(Reservation.objects.filter(flight_id=flight_id).exists())

    def test_reservation_cascade_delete_passanger(self):
        passanger_id = self.passanger.id
        self.passanger.delete()
        self.assertFalse(Reservation.objects.filter(passanger_id=passanger_id).exists())

    def test_multiple_reservations_per_flight(self):
        passanger2 = Passanger.objects.create(
            firstName="Bob",
            lastName="Brown",
            middleName="C",
            email="bob@example.com",
            phone="555-9999",
        )
        reservation2 = Reservation.objects.create(
            flight=self.flight,
            passanger=passanger2,
        )
        self.assertEqual(Reservation.objects.filter(flight=self.flight).count(), 2)


class FlightSerializerTest(TestCase):
    def test_valid_flight_data(self):
        data = {
            "flightNumber": "DL789",
            "operatingAirLines": "Delta",
            "departureCity": "ATL",
            "arrivalCity": "BOS",
            "dateOfDeparture": "2024-05-01",
            "estimatedTimeOfDeparture": "08:00:00",
        }
        serializer = FlightSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_flight_number_special_chars(self):
        data = {
            "flightNumber": "DL-789!",
            "operatingAirLines": "Delta",
            "departureCity": "ATL",
            "arrivalCity": "BOS",
            "dateOfDeparture": "2024-05-01",
            "estimatedTimeOfDeparture": "08:00:00",
        }
        serializer = FlightSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("flightNumber", serializer.errors)

    def test_missing_required_fields(self):
        serializer = FlightSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn("flightNumber", serializer.errors)
        self.assertIn("departureCity", serializer.errors)


class PassangerSerializerTest(TestCase):
    def test_valid_passanger_data(self):
        data = {
            "firstName": "Alice",
            "lastName": "Wonder",
            "middleName": "B",
            "email": "alice@test.com",
            "phone": "555-0000",
        }
        serializer = PassangerSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class FlightViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.token = Token.objects.get(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.flight = Flight.objects.create(
            flightNumber="SW100",
            operatingAirLines="Southwest",
            departureCity="DEN",
            arrivalCity="PHX",
            dateOfDeparture=datetime.date(2024, 6, 10),
            estimatedTimeOfDeparture=datetime.time(12, 0),
        )

    def test_list_flights_authenticated(self):
        response = self.client.get("/flightServices/flights/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_flights_unauthenticated(self):
        client = APIClient()
        response = client.get("/flightServices/flights/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_flight(self):
        data = {
            "flightNumber": "SW200",
            "operatingAirLines": "Southwest",
            "departureCity": "DEN",
            "arrivalCity": "SEA",
            "dateOfDeparture": "2024-07-01",
            "estimatedTimeOfDeparture": "09:00:00",
        }
        response = self.client.post("/flightServices/flights/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flight.objects.count(), 2)

    def test_retrieve_flight(self):
        response = self.client.get(f"/flightServices/flights/{self.flight.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["flightNumber"], "SW100")

    def test_update_flight(self):
        data = {
            "flightNumber": "SW100",
            "operatingAirLines": "Southwest",
            "departureCity": "DEN",
            "arrivalCity": "SFO",
            "dateOfDeparture": "2024-06-10",
            "estimatedTimeOfDeparture": "12:00:00",
        }
        response = self.client.put(
            f"/flightServices/flights/{self.flight.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.arrivalCity, "SFO")

    def test_delete_flight(self):
        response = self.client.delete(f"/flightServices/flights/{self.flight.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Flight.objects.count(), 0)


class PassangerViewSetTest(APITestCase):
    def setUp(self):
        self.passanger = Passanger.objects.create(
            firstName="Tom",
            lastName="Hanks",
            middleName="J",
            email="tom@test.com",
            phone="555-1111",
        )

    def test_list_passangers(self):
        response = self.client.get("/flightServices/passanger/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_passanger(self):
        data = {
            "firstName": "Emma",
            "lastName": "Watson",
            "middleName": "C",
            "email": "emma@test.com",
            "phone": "555-2222",
        }
        response = self.client.post("/flightServices/passanger/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Passanger.objects.count(), 2)


class ReservationViewSetTest(APITestCase):
    def setUp(self):
        self.flight = Flight.objects.create(
            flightNumber="BA300",
            operatingAirLines="British Airways",
            departureCity="LHR",
            arrivalCity="JFK",
            dateOfDeparture=datetime.date(2024, 8, 1),
            estimatedTimeOfDeparture=datetime.time(18, 0),
        )
        self.passanger = Passanger.objects.create(
            firstName="Will",
            lastName="Turner",
            middleName="D",
            email="will@test.com",
            phone="555-3333",
        )
        self.reservation = Reservation.objects.create(
            flight=self.flight,
            passanger=self.passanger,
        )

    def test_list_reservations(self):
        response = self.client.get("/flightServices/reservation/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_reservation(self):
        response = self.client.get(
            f"/flightServices/reservation/{self.reservation.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FindFlightsTest(APITestCase):
    def setUp(self):
        Flight.objects.create(
            flightNumber="AA100",
            operatingAirLines="American Airlines",
            departureCity="NYC",
            arrivalCity="LAX",
            dateOfDeparture=datetime.date(2024, 3, 15),
            estimatedTimeOfDeparture=datetime.time(10, 0),
        )
        Flight.objects.create(
            flightNumber="AA200",
            operatingAirLines="American Airlines",
            departureCity="NYC",
            arrivalCity="LAX",
            dateOfDeparture=datetime.date(2024, 3, 15),
            estimatedTimeOfDeparture=datetime.time(14, 0),
        )
        Flight.objects.create(
            flightNumber="UA300",
            operatingAirLines="United Airlines",
            departureCity="NYC",
            arrivalCity="SFO",
            dateOfDeparture=datetime.date(2024, 3, 15),
            estimatedTimeOfDeparture=datetime.time(11, 0),
        )

    def test_find_flights_matching(self):
        data = {
            "departureCity": "NYC",
            "arrivalCity": "LAX",
            "dateOfDeparture": "2024-03-15",
        }
        response = self.client.post(
            "/flightServices/findFlights/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_find_flights_no_match(self):
        data = {
            "departureCity": "NYC",
            "arrivalCity": "MIA",
            "dateOfDeparture": "2024-03-15",
        }
        response = self.client.post(
            "/flightServices/findFlights/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_find_flights_different_date(self):
        data = {
            "departureCity": "NYC",
            "arrivalCity": "LAX",
            "dateOfDeparture": "2024-03-16",
        }
        response = self.client.post(
            "/flightServices/findFlights/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class SaveReservationTest(APITestCase):
    def setUp(self):
        self.flight = Flight.objects.create(
            flightNumber="DL500",
            operatingAirLines="Delta",
            departureCity="ATL",
            arrivalCity="ORD",
            dateOfDeparture=datetime.date(2024, 9, 1),
            estimatedTimeOfDeparture=datetime.time(7, 30),
        )

    def test_save_reservation_success(self):
        data = {
            "flightId": self.flight.id,
            "firstName": "Sarah",
            "lastName": "Connor",
            "middleName": "J",
            "email": "sarah@test.com",
            "phone": "555-4444",
        }
        response = self.client.post(
            "/flightServices/saveReservation/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(Passanger.objects.count(), 1)
        reservation = Reservation.objects.first()
        self.assertEqual(reservation.flight, self.flight)
        self.assertEqual(reservation.passanger.firstName, "Sarah")

    def test_save_reservation_invalid_flight(self):
        data = {
            "flightId": 9999,
            "firstName": "Sarah",
            "lastName": "Connor",
            "middleName": "J",
            "email": "sarah@test.com",
            "phone": "555-4444",
        }
        with self.assertRaises(Flight.DoesNotExist):
            self.client.post(
                "/flightServices/saveReservation/", data, format="json"
            )


class TokenAuthTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="authuser", password="authpass123"
        )

    def test_token_created_on_user_creation(self):
        self.assertTrue(Token.objects.filter(user=self.user).exists())

    def test_obtain_token(self):
        response = self.client.post(
            "/api-token-auth/",
            {"username": "authuser", "password": "authpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_obtain_token_invalid_credentials(self):
        response = self.client.post(
            "/api-token-auth/",
            {"username": "authuser", "password": "wrongpass"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
