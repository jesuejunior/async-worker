from collections import UserDict
from enum import Enum, auto
from typing import Callable, Coroutine, Dict, List, Any

from cached_property import cached_property

from asyncworker.conf import settings
from asyncworker.options import Defaultvalues, Events, Options


RouteHandler = Callable[[], Coroutine]
Route = Dict[str, Any]


class RouteTypes(Enum):
    AMQP_RABBITMQ = auto()
    SSE = auto()


class RoutesRegistry(UserDict):
    @cached_property
    def amqp_routes(self) -> List[Dict]:
        routes = []
        for handler, route in self.items():
            if route['type'] is not RouteTypes.AMQP_RABBITMQ:
                continue
            options = route['options']
            routes.append({
                "routes": route['routes'],
                "handler": handler,
                "options": {
                    "vhost": route.get('vhost',
                                       settings.AMQP_DEFAULT_VHOST),
                    "bulk_size": options.get(Options.BULK_SIZE,
                                             Defaultvalues.BULK_SIZE),
                    "bulk_flush_interval": options.get(
                        Options.BULK_FLUSH_INTERVAL,
                        Defaultvalues.BULK_FLUSH_INTERVAL),
                    Events.ON_SUCCESS: options.get(
                        Events.ON_SUCCESS,
                        Defaultvalues.ON_SUCCESS),
                    Events.ON_EXCEPTION: options.get(
                        Events.ON_EXCEPTION,
                        Defaultvalues.ON_EXCEPTION),
                }
            })
        return routes

    @cached_property
    def sse_routes(self) -> List[Route]:
        routes = []
        for handler, route in self.items():
            if route['type'] is not RouteTypes.SSE:
                continue

            options = route['options']
            headers = route.pop('headers', {})
            default_headers = route['default_options'].get('headers', {})
            routes.append({
                "routes": route['routes'],
                "handler": handler,
                "options": {
                    "bulk_size": options.get(
                        Options.BULK_SIZE,
                        Defaultvalues.BULK_SIZE),
                    "bulk_flush_interval": options.get(
                        Options.BULK_FLUSH_INTERVAL,
                        Defaultvalues.BULK_FLUSH_INTERVAL),
                    "headers": {
                        **headers,
                        **default_headers
                    },
                }
            })
        return routes
