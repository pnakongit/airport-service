import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Order, Ticket
from airport.serializers import OrderListDetailSerializer, TicketSerializer
from airport.tests.helpers import detail_url, sample_flight, sample_airplane

ORDER_URL = reverse("airport:order-list")
ORDER_DETAIL_VIEW_NAME = "airport:order-detail"
TICKET_LIST_VIEW_NAME = "airport:order-ticket-list"
TICKET_DETAIL_VIEW_NAME = "airport:order-ticket-detail"


class UnAuthenticatedOrderAPITest(TestCase):
    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password123"
        )
        order = Order.objects.create(user=user)
        self.detail_url = detail_url(
            ORDER_DETAIL_VIEW_NAME,
            order.id
        )
        self.client = APIClient()

    def test_order_list_auth_required(self) -> None:
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_detail_auth_required(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_create_auth_required(self) -> None:
        response = self.client.post(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password1234"
        )
        self.user.is_staff = True
        self.user.save()
        self.order = Order.objects.create(user=self.user)
        self.detail_url = detail_url(
            ORDER_DETAIL_VIEW_NAME,
            self.order.pk
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_order_list(self) -> None:
        Order.objects.create(user=self.user)
        Order.objects.create(user=self.user)

        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        orders_qs = Order.objects.filter(user=self.user)
        serializer = OrderListDetailSerializer(orders_qs, many=True)

        self.assertEqual(response.data["results"], serializer.data)

    def test_order_list_is_paginated(self) -> None:
        page_size = 4
        order_count = Order.objects.filter(user=self.user).count()

        for i in range(page_size - order_count + 1):
            Order.objects.create(
                user=self.user,
            )

        first_page = Order.objects.filter(user=self.user)[:page_size]
        second_page = Order.objects.filter(user=self.user)[page_size:]

        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = OrderListDetailSerializer(first_page, many=True)
        self.assertEqual(response.data["results"], serializer.data)

        response = self.client.get(ORDER_URL + "?page=" + str(2))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = OrderListDetailSerializer(second_page, many=True)
        self.assertEqual(response.data["results"], serializer.data)

    def test_order_list_available_only_user_orders(self) -> None:
        authenticated_user = self.user
        another_user = get_user_model().objects.create_user(
            email="athoter_user@user.com",
        )
        Order.objects.create(user=authenticated_user)
        Order.objects.create(user=another_user)

        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        orders_qs = Order.objects.filter(user=self.user)
        serializer = OrderListDetailSerializer(orders_qs, many=True)

        self.assertEqual(response.data["results"], serializer.data)

    def test_order_detail(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = OrderListDetailSerializer(self.order)
        self.assertEqual(response.data, serializer.data)

    def test_order_create_add_authenticated_user_to_order(self) -> None:
        response = self.client.post(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_order = Order.objects.get(id=response.data["id"])
        self.assertEqual(created_order.user, self.user)

    def test_order_create_with_tickets(self) -> None:
        airplane = sample_airplane(rows=10, seats_in_row=10)
        flight = sample_flight(airplane=airplane)

        payload = {
            "tickets": [
                {
                    "seat": 2,
                    "row": 1,
                    "flight": flight.id
                },
                {
                    "seat": 1,
                    "row": 1,
                    "flight": flight.id
                }
            ]
        }

        response = self.client.post(
            ORDER_URL,
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_order = Order.objects.get(id=response.data["id"])

        for ticket in created_order.tickets.all():
            payload_ticket = payload["tickets"][ticket.id - 1]
            self.assertEqual(ticket.seat, payload_ticket["seat"])
            self.assertEqual(ticket.row, payload_ticket["row"])
            self.assertEqual(ticket.flight.id, payload_ticket["flight"])

    def test_order_update_method_not_allowed(self) -> None:
        response = self.client.put(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_order_delete_method_not_allowed(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class UnAuthenticatedTicketNestedViewApiTests(TestCase):
    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password123"
        )
        airplane = sample_airplane()
        flight = sample_flight(airplane=airplane)
        order = Order.objects.create(
            user=user,
        )
        ticket = Ticket.objects.create(
            seat=1,
            row=1,
            flight=flight,
            order=order
        )
        self.list_url = reverse(
            TICKET_LIST_VIEW_NAME,
            kwargs={"order_pk": order.pk}
        )
        self.detail_url = reverse(
            TICKET_DETAIL_VIEW_NAME,
            kwargs={
                "order_pk": order.pk,
                "pk": ticket.pk
            }
        )
        self.client = APIClient()

    def test_ticket_list_auth_required(self) -> None:
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ticket_detail_auth_required(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ticket_create_auth_required(self) -> None:
        response = self.client.post(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTicketNestedViewApiTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email="user@user.com",
            password="password123"
        )
        airplane = sample_airplane()
        self.flight = sample_flight(airplane=airplane)
        self.order = Order.objects.create(
            user=self.user,
        )
        self.ticket = Ticket.objects.create(
            seat=1,
            row=1,
            flight=self.flight,
            order=self.order
        )
        self.list_url = reverse(
            TICKET_LIST_VIEW_NAME,
            kwargs={"order_pk": self.order.pk}
        )
        self.detail_url = reverse(
            TICKET_DETAIL_VIEW_NAME,
            kwargs={
                "order_pk": self.order.pk,
                "pk": self.ticket.pk
            }
        )
        self.payload = {
            "seat": 1,
            "row": 2,
            "flight": self.flight.id,
        }
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_ticket_list(self) -> None:
        order = self.order
        flight = self.flight

        Ticket.objects.create(
            seat=2,
            row=1,
            flight=flight,
            order=order
        )
        Ticket.objects.create(
            seat=3,
            row=1,
            flight=flight,
            order=order
        )

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tickets = Ticket.objects.filter(order=order)
        serializer = TicketSerializer(tickets, many=True)
        self.assertEqual(response.data["results"], serializer.data)

    def test_ticket_list_is_paginated(self) -> None:
        page_size = 4
        order = self.order
        flight = self.flight
        tickets_count = Ticket.objects.filter(order=self.order).count()

        for i in range(page_size - tickets_count + 1):
            Ticket.objects.create(
                seat=1 + i,
                row=2,
                flight=flight,
                order=order
            )

        first_page = Ticket.objects.filter(order=order)[:page_size]
        second_page = Ticket.objects.filter(order=order)[page_size:]

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = TicketSerializer(first_page, many=True)
        self.assertEqual(response.data["results"], serializer.data)

        response = self.client.get(self.list_url + "?page=" + str(2))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = TicketSerializer(second_page, many=True)
        self.assertEqual(response.data["results"], serializer.data)

    def test_in_ticket_list_available_only_user_tickets(self) -> None:
        flight = self.flight
        auth_user = self.user
        auth_user_order = self.order
        another_user = get_user_model().objects.create_user(
            email="another_user@user.com",
            password="password123"
        )
        another_user_order = Order.objects.create(
            user=another_user
        )
        Ticket.objects.create(
            seat=2,
            row=1,
            flight=flight,
            order=auth_user_order
        )
        Ticket.objects.create(
            seat=3,
            row=1,
            flight=flight,
            order=another_user_order
        )

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tickets = Ticket.objects.filter(order__user=auth_user)
        serializer = TicketSerializer(tickets, many=True)
        self.assertEqual(response.data["results"], serializer.data)

    def test_in_ticket_list_available_tickets_of_order_from_url(self) -> None:
        flight = self.flight
        order_from_url = self.order
        another_order_same_user = Order.objects.create(
            user=order_from_url.user
        )

        Ticket.objects.create(
            seat=2,
            row=1,
            flight=flight,
            order=order_from_url
        )
        Ticket.objects.create(
            seat=3,
            row=1,
            flight=flight,
            order=another_order_same_user
        )

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tickets = Ticket.objects.filter(order=order_from_url)
        serializer = TicketSerializer(tickets, many=True)
        self.assertEqual(response.data["results"], serializer.data)

    def test_ticket_create(self) -> None:
        response = self.client.post(self.list_url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_ticket = Ticket.objects.get(pk=response.data["id"])
        serializer = TicketSerializer(created_ticket)

        for key, value in self.payload.items():
            self.assertEqual(serializer.data[key], value)

    def test_user_can_crete_ticket_only_for_own_order(self) -> None:
        another_user = get_user_model().objects.create_user(
            email="antother_user@antother.com",
            password="password123"
        )
        another_user_order = Order.objects.create(
            user=another_user
        )
        list_url_with_another_user_order = reverse(
            TICKET_LIST_VIEW_NAME,
            kwargs={"order_pk": another_user_order.pk}
        )

        response = self.client.post(list_url_with_another_user_order, self.payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ticket_create_add_ticket_to_order_from_url(self) -> None:
        response = self.client.post(self.list_url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_ticket = Ticket.objects.get(pk=response.data["id"])

        self.assertEqual(created_ticket.order, self.order)

    def test_ticket_detail(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = TicketSerializer(self.ticket)
        self.assertEqual(response.data, serializer.data)

    def test_ticket_update(self) -> None:
        ticket = self.ticket
        payload = {
            "seat": ticket.seat + 1,
            "row": ticket.row + 1,
            "flight": ticket.flight.id,
        }

        response = self.client.put(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_ticket = Ticket.objects.get(pk=response.data["id"])
        serializer = TicketSerializer(updated_ticket)
        for key, value in payload.items():
            self.assertEqual(serializer.data[key], value)

    def test_user_can_update_ticket_only_from_own_order(self) -> None:
        another_user = get_user_model().objects.create_user(
            email="antother_user@antother.com",
            password="password123"
        )
        another_user_order = Order.objects.create(
            user=another_user
        )

        detail_url_with_another_user_order = reverse(
            TICKET_DETAIL_VIEW_NAME,
            kwargs={
                "order_pk": another_user_order.pk,
                "pk": another_user_order.pk
            }
        )

        response = self.client.put(detail_url_with_another_user_order, self.payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ticket_delete(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ticket.objects.filter(pk=self.ticket.pk).exists())

    def test_user_can_delete_ticket_only_from_own_order(self) -> None:
        another_user = get_user_model().objects.create_user(
            email="antother_user@antother.com",
            password="password123"
        )
        another_user_order = Order.objects.create(
            user=another_user
        )

        detail_url_with_another_user_order = reverse(
            TICKET_DETAIL_VIEW_NAME,
            kwargs={
                "order_pk": another_user_order.pk,
                "pk": another_user_order.pk
            }
        )

        response = self.client.delete(detail_url_with_another_user_order)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
