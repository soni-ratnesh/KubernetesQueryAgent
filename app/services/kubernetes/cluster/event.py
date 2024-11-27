"""
1. List all events in the 'default' namespace.
2. Show events related to pod 'my-pod'.
3. What are the recent events in namespace 'kube-system'?
4. Find warning events in the cluster.
5. Show events related to node 'node-1'.
6. What are the events associated with deployment 'my-deployment'?
7. List events with reason 'FailedScheduling'.
8. Find events of type 'Warning' in the 'production' namespace.
9. Get the last 10 events in the cluster.
10. Show events related to service 'my-service'.
11. List events for ReplicaSet 'my-replicaset' in namespace 'staging'.
12. Find events of type 'Normal' for namespace 'default'.
13. Show recent events related to PersistentVolumeClaim 'data-pvc'.
14. What are the latest 5 events in 'kube-system' namespace?
15. List events with reason 'BackOff' for pod 'db-pod'.

"""


from typing import Optional, Dict
from kubernetes import client
from ..kubernetes_client import KubernetesBase

class EventResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace=namespace, labels=labels)
        self.api = client.CoreV1Api()  # CoreV1Api client for Events

    def list_events(self) -> str:
        """List all events in the namespace or cluster."""
        try:
            if self.namespace:
                events = self.api.list_namespaced_event(namespace=self.namespace)
            else:
                events = self.api.list_event_for_all_namespaces()
            if not events.items:
                return "No events found."

            event_list = []
            for event in events.items:
                timestamp = event.last_timestamp or event.event_time or event.metadata.creation_timestamp
                timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'N/A'
                message = event.message
                event_info = f"[{timestamp_str}] {event.type} {event.reason}: {message}"
                event_list.append(event_info)

            return "\n".join(event_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing events"

    def list_events_for_object(self, kind: str, name: str) -> str:
        """List events related to a specific object."""
        try:
            field_selector = f"involvedObject.kind={kind},involvedObject.name={name}"
            if self.namespace:
                events = self.api.list_namespaced_event(namespace=self.namespace, field_selector=field_selector)
            else:
                events = self.api.list_event_for_all_namespaces(field_selector=field_selector)
            if not events.items:
                return f"No events found for {kind} '{name}'."

            event_list = []
            for event in events.items:
                timestamp = event.last_timestamp or event.event_time or event.metadata.creation_timestamp
                timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'N/A'
                message = event.message
                event_info = f"[{timestamp_str}] {event.type} {event.reason}: {message}"
                event_list.append(event_info)

            return f"Events for {kind} '{name}':\n" + "\n".join(event_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving events for {kind} '{name}'"

    def list_events_by_reason(self, reason: str) -> str:
        """List events filtered by reason."""
        try:
            field_selector = f"reason={reason}"
            if self.namespace:
                events = self.api.list_namespaced_event(namespace=self.namespace, field_selector=field_selector)
            else:
                events = self.api.list_event_for_all_namespaces(field_selector=field_selector)
            if not events.items:
                return f"No events found with reason '{reason}'."

            event_list = []
            for event in events.items:
                timestamp = event.last_timestamp or event.event_time or event.metadata.creation_timestamp
                timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'N/A'
                message = event.message
                involved_obj = f"{event.involved_object.kind}/{event.involved_object.name}"
                event_info = f"[{timestamp_str}] {event.type} {reason} on {involved_obj}: {message}"
                event_list.append(event_info)

            return f"Events with reason '{reason}':\n" + "\n".join(event_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving events with reason '{reason}'"

    def list_events_by_type(self, event_type: str) -> str:
        """List events filtered by event type (e.g., Normal, Warning)."""
        try:
            field_selector = f"type={event_type}"
            if self.namespace:
                events = self.api.list_namespaced_event(namespace=self.namespace, field_selector=field_selector)
            else:
                events = self.api.list_event_for_all_namespaces(field_selector=field_selector)
            if not events.items:
                return f"No events of type '{event_type}' found."

            event_list = []
            for event in events.items:
                timestamp = event.last_timestamp or event.event_time or event.metadata.creation_timestamp
                timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'N/A'
                message = event.message
                involved_obj = f"{event.involved_object.kind}/{event.involved_object.name}"
                event_info = f"[{timestamp_str}] {event_type} {event.reason} on {involved_obj}: {message}"
                event_list.append(event_info)

            return f"Events of type '{event_type}':\n" + "\n".join(event_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving events of type '{event_type}'"

    def list_recent_events(self, count: int = 10) -> str:
        """Get the most recent events."""
        try:
            if self.namespace:
                events = self.api.list_namespaced_event(namespace=self.namespace)
            else:
                events = self.api.list_event_for_all_namespaces()
            if not events.items:
                return "No events found."

            # Sort events by timestamp descending
            events.items.sort(key=lambda e: e.last_timestamp or e.event_time or e.metadata.creation_timestamp, reverse=True)
            recent_events = events.items[:count]

            event_list = []
            for event in recent_events:
                timestamp = event.last_timestamp or event.event_time or event.metadata.creation_timestamp
                timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'N/A'
                message = event.message
                involved_obj = f"{event.involved_object.kind}/{event.involved_object.name}"
                event_info = f"[{timestamp_str}] {event.type} {event.reason} on {involved_obj}: {message}"
                event_list.append(event_info)

            return f"Most recent {count} events:\n" + "\n".join(event_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving recent events"


def event_handler(query) -> str:
    event_resource = EventResource(namespace=query.namespace)

    # Route based on the action specified in the query
    if query.action == "list":
        if query.filters and query.filters.reason:
            return event_resource.list_events_by_reason(query.filters.reason)
        elif query.filters and query.filters.event_type:
            return event_resource.list_events_by_type(query.filters.event_type)
        elif query.filters and query.filters.count:
            return event_resource.list_recent_events(query.filters.count)
        else:
            return event_resource.list_events()

    elif query.action == "list_for_object" and query.filters and query.filters.involved_object_kind and query.filters.involved_object_name:
        return event_resource.list_events_for_object(query.filters.involved_object_kind, query.filters.involved_object_name)

    else:
        return "Unsupported action or missing required parameters for events."
