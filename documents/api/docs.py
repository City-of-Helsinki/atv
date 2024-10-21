from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status

from documents.serializers import AttachmentSerializer, DocumentSerializer
from documents.serializers.document import DocumentMetadataSerializer, GDPRSerializer
from documents.serializers.status_history import (
    CreateStatusHistorySerializer,
    StatusHistorySerializer,
)

error_serializer = inline_serializer(
    "ErrorResponse",
    fields={
        "errors": inline_serializer(
            "Error",
            fields={
                "code": serializers.CharField(),
                "description": serializers.CharField(),
            },
            many=True,
        )
    },
)

example_error = OpenApiExample(
    name="ErrorExample",
    response_only=True,
    status_codes=[
        str(status.HTTP_400_BAD_REQUEST),
        str(status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
    value={
        "errors": [
            {
                "code": "GENERAL_ERROR",
                "description": "Something went wrong, we don't know what.",
            }
        ]
    },
)

example_attachment = OpenApiExample(
    name="AttachmentExample",
    response_only=True,
    status_codes=[str(status.HTTP_200_OK), str(status.HTTP_201_CREATED)],
    value={
        "id": 12994,
        "createdAt": "2021-04-21T13:17:15.511Z",
        "updatedAt": "2021-04-21T13:17:15.511Z",
        "filename": "high-school-diploma.pdf",
        "mediaType": "application/pdf",
        "size": 123223,
        "href": "https://transactions-storage.com/api/v1/documents/97c0b7a5-0b4c-4470-9a41-48d79454f233/"
        "attachments/12994",
    },
)

example_document = OpenApiExample(
    name="DocumentExample",
    response_only=True,
    status_codes=[str(status.HTTP_200_OK), str(status.HTTP_201_CREATED)],
    value={
        "id": "f6fe8acc-3b91-41b3-a176-9d2feab2d2bb",
        "created_at": "2022-03-07T16:08:39.580394+02:00",
        "updated_at": "2022-03-07T17:59:39.580394+02:00",
        "status": {
            "value": "PROCESSING",
            "status_display_values": {"fi": "Käsittelyssä"},
            "timestamp": "2022-06-21T13:13:54.247974+03:00",
            "activities": [
                {
                    "title": {"fi": "Otsikko"},
                    "message": {"fi": "Viestin teksti"},
                    "activity_links": {
                        "en": {
                            "url": "asdf.uk",
                            "display_text": "continue in service asdf",
                        },
                        "fi": {
                            "url": "asdf.fi",
                            "display_text": "tästä palveluun asdf",
                        },
                        "sv": {"url": "asdf.sv", "display_text": "samma på svenska"},
                    },
                    "activity_timestamp": "2023-05-22T15:29:49.384845+03:00",
                    "show_to_user": True,
                }
            ],
        },
        "status_histories": [
            {
                "value": "PROCESSING",
                "status_display_values": {"fi": "Käsittelyssä"},
                "timestamp": "2022-06-21T13:13:54.247974+03:00",
                "activities": [
                    {
                        "title": {"fi": "Otsikko"},
                        "message": {"fi": "Viestin teksti"},
                        "activity_links": {
                            "en": {
                                "url": "asdf.uk",
                                "display_text": "continue in service asdf",
                            },
                            "fi": {
                                "url": "asdf.fi",
                                "display_text": "tästä palveluun asdf",
                            },
                            "sv": {
                                "url": "asdf.sv",
                                "display_text": "samma på svenska",
                            },
                        },
                        "activity_timestamp": "2023-05-22T15:29:49.384845+03:00",
                        "show_to_user": True,
                    }
                ],
            },
            {
                "value": "RECEIVED",
                "status_display_values": {"fi": "Vastaanotettu"},
                "timestamp": "2022-06-21T13:13:54.247974+03:00",
                "activities": [],
            },
            {
                "value": "SUBMITTED",
                "status_display_values": {"fi": "Lähetetty"},
                "timestamp": "2022-06-21T13:13:54.247974+03:00",
                "activities": [],
            },
        ],
        "type": "APPLICATION_FOR_RESIDENTIAL_PARKING_PERMIT",
        "human_readable_type": {"en": "Form", "fi": "Lomake"},
        "service": "Parking Permits",
        "user_id": "97c0b7a5-0b4c-4470-9a41-48d79454f233",
        "transaction_id": "some transaction id 1234",
        "business_id": "0874691-5",
        "tosFunction_id": "eb30af1d9d654ebc98287ca25f231bf6",
        "tosRecord_id": "521317ab6b4a4157a1714f5cc9fd69de",
        "metadata": {
            "some-field": "some value relevant to the calling service",
            "status": "some-arbitrary-status",
            "handler": "sstallone",
        },
        "draft": True,
        "locked_after": "2021-08-01T00:00:00.0Z",
        "deletable": False,
        "delete_after": "2030-12-12",
        "document_language": "fi",
        "content_schema_url": "https://exampleurl.fi",
        "content": {
            "formData": {
                "firstName": "Dolph",
                "lastName": "Lundgren",
                "birthDate": "3.11.1957",
            },
            "reasonForApplication": "No reason, just testing",
        },
        "attachments": [
            {
                "id": 12994,
                "createdAt": "2021-04-21T13:17:15.511Z",
                "updatedAt": "2021-04-21T13:17:15.511Z",
                "filename": "high-school-diploma.pdf",
                "mediaType": "application/pdf",
                "size": 123223,
                "href": "https://transactions-storage.com/api/v1/documents/97c0b7a5-0b4c-4470-9a41-48d79454f233/"
                "attachments/12994",
            },
            {
                "id": 12995,
                "createdAt": "2021-04-21T13:17:25.511Z",
                "updatedAt": "2021-04-21T13:17:25.511Z",
                "filename": "my-face.jpeg",
                "mediaType": "image/jpeg",
                "size": 512884,
                "href": "https://transactions-storage.com/api/v1/documents/97c0b7a5-0b4c-4470-9a41-48d79454f233/"
                "attachments/12995",
            },
        ],
    },
)

example_document_metadata = OpenApiExample(
    name="DocumentMetadataExample",
    response_only=True,
    status_codes=[str(status.HTTP_200_OK), str(status.HTTP_201_CREATED)],
    value={
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": "cf1bf707-5fef-4d21-841a-3408e5f1ea66",
                "type": "mysterious form",
                "human_readable_type": {},
                "created_at": "2023-05-15T17:00:08.961578+03:00",
                "updated_at": "2023-05-22T15:29:49.387682+03:00",
                "service": {
                    "name": "TestService",
                    "display_names": {
                        "en": "Test Service",
                        "fi": "Testi Palvelu",
                        "sv": "Samma på svenska",
                    },
                    "service_link": "https://example.hel.fi",
                },
                "status": {
                    "value": "RECEIVED",
                    "status_display_values": {"fi": "Vastaanotettu"},
                    "timestamp": "2023-05-22T15:29:49.379761+03:00",
                    "activities": [
                        {
                            "title": {"fi": "Otsikko"},
                            "message": {"fi": "Viestin teksti"},
                            "activity_links": {
                                "en": {
                                    "url": "asdf.uk",
                                    "display_text": "continue in service asdf",
                                },
                                "fi": {
                                    "url": "asdf.fi",
                                    "display_text": "tästä palveluun asdf",
                                },
                                "sv": {
                                    "url": "asdf.sv",
                                    "display_text": "samma på svenska",
                                },
                            },
                            "activity_timestamp": "2023-05-22T15:29:49.384845+03:00",
                            "show_to_user": True,
                        }
                    ],
                },
                "status_histories": [
                    {
                        "value": "RECEIVED",
                        "status_display_values": {"fi": "Vastaanotettu"},
                        "timestamp": "2023-05-22T15:29:49.379761+03:00",
                        "activities": [
                            {
                                "title": {"fi": "Otsikko"},
                                "message": {"fi": "Viestin teksti"},
                                "activity_links": {
                                    "en": {
                                        "url": "asdf.uk",
                                        "display_text": "continue in service asdf",
                                    },
                                    "fi": {
                                        "url": "asdf.fi",
                                        "display_text": "tästä palveluun asdf",
                                    },
                                    "sv": {
                                        "url": "asdf.sv",
                                        "display_text": "samma på svenska",
                                    },
                                },
                                "activity_timestamp": "2023-05-22T15:29:49.384845+03:00",
                                "show_to_user": True,
                            }
                        ],
                    }
                ],
                "delete_after": "2026-12-12",
                "document_language": "fi",
                "content_schema_url": "https://example.hel.fi",
            }
        ],
    },
)
example_statistics_data = OpenApiExample(
    name="DocumentExample",
    response_only=True,
    status_codes=[str(status.HTTP_200_OK), str(status.HTTP_201_CREATED)],
    value={
        "id": "f6fe8acc-3b91-41b3-a176-9d2feab2d2bb",
        "created_at": "2022-03-07T16:08:39.580394+02:00",
        "user_id": "g6fe8acc-3b91-41b3-a176-9d2feab2d2ba",
        "service": "Parking Permits",
        "transaction_id": "TRANSACTION123",
        "type": "APPLICATION_FOR_RESIDENTIAL_PARKING_PERMIT",
        "human_readable_type": {"en": "Form", "fi": "Lomake"},
        "status": "PROCESSING",
        "deletable": True,
        "attachments": ["attachment1.pdf", "attachment2.docs"],
        "attachment_count": 2,
    },
)

example_gdpr_api_repsonse = OpenApiExample(
    name="GDPR List Response",
    status_codes=[str(status.HTTP_200_OK), str(status.HTTP_204_NO_CONTENT)],
    value={
        "data": {
            "total_deletable": 0,
            "total_undeletable": 1,
            "documents": [
                {
                    "id": "0576d4e7-a84d-411f-9285-bf7dcc864ae0",
                    "created_at": "2022-06-27T17:51:59.374880+03:00",
                    "user_id": "a67dec08-cc7c-11ec-a4fb-00155dcd8647",
                    "service": "TestService",
                    "type": "mysterious form",
                    "human_readable_type": {"en": "Mysterious Form"},
                    "deletable": True,
                    "delete_after": "2030-12-12",
                    "attachment_count": 0,
                    "attachments": [],
                },
                {
                    "id": "05d3497b-b5ab-46c4-a7bf-5b6cbfc344b0",
                    "created_at": "2022-06-09T17:16:49.565282+03:00",
                    "user_id": "a67dec08-cc7c-11ec-a4fb-00155dcd8647",
                    "service": "TestService",
                    "type": "mysterious form",
                    "human_readable_type": {},
                    "deletable": False,
                    "delete_after": "2030-12-12",
                    "attachment_count": 1,
                    "attachments": ["myfavoritesong.mp3"],
                },
            ],
        }
    },
)

example_create_status_activity_data = OpenApiExample(
    name="DocumentStatusExampleCreate",
    response_only=True,
    status_codes=[str(status.HTTP_201_CREATED)],
    value={
        "value": "RECEIVED",
        "status_display_values": {"fi": "Vastaanotettu"},
        "timestamp": "2023-05-22T15:29:49.379761+03:00",
        "activities": [
            {
                "title": {"fi": "Otsikko"},
                "message": {"fi": "Viestin teksti"},
                "activity_links": {
                    "en": {
                        "url": "asdf.uk",
                        "display_text": "continue in service asdf",
                    },
                    "fi": {"url": "asdf.fi", "display_text": "tästä palveluun asdf"},
                    "sv": {"url": "asdf.sv", "display_text": "samma på svenska"},
                },
                "activity_timestamp": "2023-05-22T15:29:49.384845+03:00",
                "show_to_user": True,
            }
        ],
    },
)

example_get_status_activity_data = OpenApiExample(
    name="DocumentStatusExampleGet",
    status_codes=[str(status.HTTP_200_OK)],
    response_only=True,
    value={
        "value": "RECEIVED",
        "status_display_values": {"fi": "Vastaanotettu"},
        "timestamp": "2023-05-22T15:29:49.379761+03:00",
        "activities": [
            {
                "title": {"fi": "Otsikko"},
                "message": {"fi": "Viestin teksti"},
                "activity_links": {
                    "en": {
                        "url": "asdf.uk",
                        "display_text": "continue in service asdf",
                    },
                    "fi": {"url": "asdf.fi", "display_text": "tästä palveluun asdf"},
                    "sv": {"url": "asdf.sv", "display_text": "samma på svenska"},
                },
                "activity_timestamp": "2023-05-22T15:29:49.384845+03:00",
                "show_to_user": True,
            }
        ],
    },
)


def _base_401_response(custom_message: str = None) -> OpenApiResponse:
    return OpenApiResponse(
        description=custom_message
        or "Request’s credentials are missing or invalid. A valid JWT authentication is required.",
    )


def _base_400_response(custom_message: str = None) -> OpenApiResponse:
    return OpenApiResponse(
        response=error_serializer,
        description=custom_message
        or "One or more of the given parameters were invalid.",
    )


def _base_500_response(custom_message: str = None) -> OpenApiResponse:
    return OpenApiResponse(
        response=error_serializer,
        description=custom_message
        or "There has been an unexpected error during the call.",
    )


attachment_viewset_docs = {
    "retrieve": extend_schema(
        summary="Download a document's attachment",
        description="Permission to access the attachment is checked based on the containing document as follows:\n"
        "* Admin users are allowed access to the attachment if the containing document was stored using the service "
        "they are using and whose admins they are.\n"
        "* Authenticated users are allowed access to the attachment if they are the owner of the containing document.",
        # TODO: Uncomment when organization features are implemented
        # " or the containing document is owned by an organization and the user has permission to act on behalf "
        # "of that organization.",
        responses={
            (status.HTTP_200_OK, "application/octet-stream"): OpenApiResponse(
                description="Returns the attachment as a downloadable file.",
            ),
            (status.HTTP_400_BAD_REQUEST, "application/json"): _base_400_response(),
            status.HTTP_401_UNAUTHORIZED: _base_401_response(),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description="The authenticated user lacks the proper permissions to access the document. "
                "Depending on the requested document, "
                "either the user does not belong to the admin group of the service which owns the document, "
                "the user does not own the document."
                # TODO: Uncomment when organization features are implemented
                # " or the user does not have permission to act on behalf "
                # "of the organization which owns the document."
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="No document was found with `documentId` or the document did not have "
                "an attachment `attachmentId`."
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: _base_500_response(),
        },
        examples=[example_attachment, example_error],
    ),
    "create": extend_schema(
        summary="Upload a new attachment to a document",
        description="Permission to access the document is checked as follows:\n"
        "* Authenticated users are allowed access to the document if they are the owner of the document.\n\n"
        # TODO: Uncomment when organization features are implemented
        # " or the document is owned by an organization and the user has permission to act on behalf "
        # "of that organization.\n\n"
        "The following rules apply:\n"
        "* Drafts may be modified by the owning user or the owning service's admin\n"
        # TODO: Uncomment when organization features are implemented
        #   Replace the previous line with the following
        # "* Drafts may be modified by the owning user, "
        # "the owning service's admin or an organization's representative, "
        # "if the document is owned by an organization.\n"
        "* Non-drafts may be modified by an admin.\n"
        "* Documents may not be modified if their `lockedAfter` date has passed.",
        request={"application/octet-stream": OpenApiTypes.BINARY},
        responses={
            (status.HTTP_201_CREATED, "application/json"): OpenApiResponse(
                response=AttachmentSerializer,
                description="The attachment was uploaded successfully. "
                "The attachments information is returned in the response body.",
            ),
            (status.HTTP_400_BAD_REQUEST, "application/json"): _base_400_response(),
            status.HTTP_401_UNAUTHORIZED: _base_401_response(),
            # TODO: Uncomment when organization features are implemented
            # status.HTTP_403_FORBIDDEN: OpenApiResponse(
            #     description="The request contains an organization ID and the currently authenticated user "
            #     "does not have permission to act on behalf of that organization."
            # ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: _base_500_response(),
        },
        examples=[example_attachment, example_error],
    ),
    "destroy": extend_schema(
        summary="Remove a document's attachment",
        description="Permission to remove the attachment is checked based on the containing document as follows:\n"
        "* Authenticated users are allowed to remove the attachment if they are the owner "
        "of the containing document.\n\n"
        # TODO: Uncomment when organization features are implemented
        # "or the containing document is owned by an organization and the user has permission to act on behalf "
        # "of that organization.\n\n"
        "The following rules apply:\n"
        "* Attachments of drafts may be removed by the owning user."
        # TODO: Uncomment when organization features are implemented
        # "or an organization's representative, "
        # "if the containing document is owned by an organization."
        "* Attachments may not be removed if the containing document's `lockedAfter` date has passed. "
        "This should be done by removing the whole document.",
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description="The attachment was removed successfully.",
            ),
            (status.HTTP_400_BAD_REQUEST, "application/json"): _base_400_response(),
            status.HTTP_401_UNAUTHORIZED: _base_401_response(),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description="The authenticated user lacks the proper permissions to access the document. "
                "Depending on the requested document, "
                "either the user does not belong to the admin group of the service which owns the document "
                "or the user does not own the document."
                # TODO: Uncomment when organization features are implemented
                #   Replace the previous two lines with the following
                # "either the user does not belong to the admin group of the service which owns the document, "
                # "the user does not own the document or the user does not have permission to act on behalf "
                # "of the organization which owns the document."
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="No document was found with `documentId` or the document did not have "
                "an attachment `attachmentId`."
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: _base_500_response(),
        },
        examples=[example_error],
    ),
    # Not implementing
    "list": extend_schema(exclude=True),
    "update": extend_schema(exclude=True),
    "partial_update": extend_schema(exclude=True),
}

document_viewset_docs = {
    "list": extend_schema(
        summary="Search for documents",
        description="This endpoint can be used to fetch a list of documents. "
        "The list can be filtered, sorted and paged using the appropriate query parameters.\n\n"
        "The results will contain only those documents which are allowed for the current user.\n\n"
        "* Admin users are allowed to fetch all documents which were stored using the service "
        "they are using and whose admins they are.\n"
        "* Authenticated users are allowed to fetch documents which are owned by them and "
        "which were stored using the service they are using.",
        # TODO: Uncomment when organization features are implemented
        # "Documents owned by an organization are not returned even if such a document
        # "was created by the current user.\n"
        # "* Authenticated users may fetch documents owned by an organization by giving the organization's business ID "
        # "in the search parameters. In this case the user's permission to act on behalf of the organization "
        # "is verified and the results will contain only documents which are owned by the given organization.",
        parameters=[
            OpenApiParameter(
                "status",
                OpenApiTypes.STR,
                description="Search for documents with the given status",
            ),
            OpenApiParameter(
                "type",
                OpenApiTypes.STR,
                description="Search for documents with the given type",
            ),
            OpenApiParameter(
                "business_id",
                OpenApiTypes.STR,
                description="Search for documents which are owned by the given business ID. "
                "If this is given, the calling user must either be an admin",
                # TODO: Uncomment when organization features are implemented
                #   Replace the previous line with the following
                # "If this is given, the calling user must either be an admin or have permission to act "
                # "on behalf of the organization",
            ),
            OpenApiParameter(
                "user_id",
                OpenApiTypes.UUID,
                description="Search for documents which are owned by the given user ID. "
                "If this is given, the calling user must be an admin of the service",
            ),
            OpenApiParameter(
                "transaction_id",
                OpenApiTypes.STR,
                description="Search for documents with the given transaction id",
            ),
            OpenApiParameter(
                "lookfor",
                OpenApiTypes.STR,
                description="Search for documents with metadata matching key:value pairs separated by comma."
                " ( key:value, key:value )."
                " Lookup method for value is 'iexact', key must be exact and is case sensitive.",
            ),
        ],
        responses={
            (status.HTTP_200_OK, "application/json"): OpenApiResponse(
                response=DocumentSerializer,
                description="Returns a list of documents with the given criteria. "
                "An empty list is returned if there are no results.",
            ),
            (status.HTTP_400_BAD_REQUEST, "application/json"): _base_400_response(),
            status.HTTP_401_UNAUTHORIZED: _base_401_response(),
            # TODO: Uncomment when organization features are implemented
            # status.HTTP_403_FORBIDDEN: OpenApiResponse(
            #     description="The search parameters contain an organization ID "
            #     "and the currently authenticated user does"
            #     "not have permission to act on behalf of that organization."
            # ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: _base_500_response(),
        },
        examples=[example_document, example_error],
    ),
    "retrieve": extend_schema(
        summary="Fetch a document by ID",
        description="This endpoint allows a user to fetch a document's details.\n\n"
        "Permission to access the document is checked as follows:\n\n"
        "* Admin users are allowed access to the document if it was stored using the service "
        "they are using and whose admins they are.\n"
        "* Authenticated users are allowed access to the document if they are the owner of the document.",
        # TODO: Uncomment when organization features are implemented
        #   Replace the previous line with the following
        # "* Authenticated users are allowed access to the document if they are the owner of the document "
        # "or the document is owned by an organization and the user has permission to act on behalf "
        # "of that organization.",
        responses={
            (status.HTTP_200_OK, "application/json"): OpenApiResponse(
                response=DocumentSerializer,
                description="The document was found and its contents are returned as JSON.",
            ),
            (status.HTTP_400_BAD_REQUEST, "application/json"): _base_400_response(),
            status.HTTP_401_UNAUTHORIZED: _base_401_response(),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description="The authenticated user lacks the proper permissions to access the document. "
                "Depending on the requested document, "
                "either the user does not belong to the admin group of the service which owns the document, "
                "the user does not own the document."
                # TODO: Uncomment when organization features are implemented
                # " or the user does not have permission to act on behalf "
                # "of the organization which owns the document."
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="No document was found with `documentId`.",
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: _base_500_response(),
        },
        examples=[example_document, example_error],
    ),
    "batch_list": extend_schema(
        summary="Fetch multiple documents by IDs",
        description="This endpoint allows a service to fetch multiple documents by their IDs",
        # TODO: Uncomment when organization features are implemented
        #   Replace the previous line with the following
        # "* Authenticated users are allowed access to the document if they are the owner of the document "
        # "or the document is owned by an organization and the user has permission to act on behalf "
        # "of that organization.",
        request=serializers.JSONField(),
        responses={
            (status.HTTP_200_OK, "application/json"): OpenApiResponse(
                response=DocumentSerializer,
                description="The document/s was found and contents are returned as JSON.",
            ),
            (status.HTTP_400_BAD_REQUEST, "application/json"): _base_400_response(),
            status.HTTP_401_UNAUTHORIZED: _base_401_response(),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description="The authenticated user lacks the proper permissions to access the document. "
                "Depending on the requested document, "
                "either the user does not belong to the admin group of the service which owns the document, "
                "the user does not own the document."
                # TODO: Uncomment when organization features are implemented
                # " or the user does not have permission to act on behalf "
                # "of the organization which owns the document."
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="No document was found with `documentId`.",
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: _base_500_response(),
        },
    ),
    "create": extend_schema(
        summary="Store a new document and its attachments",
        description="Store a new document and its attachments.\n\n"
        "This endpoint supports API key authentication to enable unauthenticated users to store documents. "
        "Note that if this endpoint is used in such a way, accessing the stored documents later "
        "will only be possible using the appropriate admin credentials.\n\n"
        "This endpoint also supports authentication using a Bearer token, similarly to the other endpoints. "
        "In this case the authenticated user is able to access the stored document normally afterwards.",
        responses={
            (status.HTTP_201_CREATED, "application/json"): OpenApiResponse(
                response=DocumentSerializer,
                description="The document was created successfully. "
                "The created document is returned in the response body.",
            ),
            (status.HTTP_400_BAD_REQUEST, "application/json"): _base_400_response(),
            status.HTTP_401_UNAUTHORIZED: _base_401_response(),
            # TODO: Uncomment when organization features are implemented
            # status.HTTP_403_FORBIDDEN: OpenApiResponse(
            #     description="The request contains an organization ID and the currently authenticated user "
            #     "does not have permission to act on behalf of that organization."
            # ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: _base_500_response(),
        },
        examples=[example_document, example_error],
    ),
    "partial_update": extend_schema(
        summary="Update an existing document",
        description="Permission to access the document is checked as follows:\n\n"
        "* Admin users are allowed access to the document if it was stored using the service they are using "
        "and whose admins they are.\n"
        "* Authenticated users are allowed access to the document if they are the owner of the document.\n\n"
        # TODO: Uncomment when organization features are implemented
        #   Replace the previous line with the following
        # "* Authenticated users are allowed access to the document if they are the owner of the document "
        # "or the document is owned by an organization and the user has permission to act "
        # "on behalf of that organization.\n\n"
        "The following rules apply:\n"
        "* Drafts may be modified by the owning user or the owning service's admin.\n"
        # TODO: Uncomment when organization features are implemented
        #   Replace the previous line with the following
        # "* Drafts may be modified by the owning user, the owning service's admin "
        # "or an organization's representative, "
        # "if the document is owned by an organization.\n"
        "* Non-drafts may be modified by an admin.\n"
        "* Documents may not be modified if their `lockedAfter` date has passed.",
        responses={
            (status.HTTP_200_OK, "application/json"): OpenApiResponse(
                response=DocumentSerializer,
                description="The Document was updated successfully. "
                "The updated contents are returned in the response body.",
            ),
            (status.HTTP_400_BAD_REQUEST, "application/json"): _base_400_response(),
            status.HTTP_401_UNAUTHORIZED: _base_401_response(),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description="The authenticated user lacks the proper permissions to access the document. "
                "Depending on the requested document, "
                "either the user does not belong to the admin group of the service which owns the document, "
                "the user does not own the document."
                # TODO: Uncomment when organization features are implemented
                # " or the user does not have permission to act on behalf "
                # "of the organization which owns the document."
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="No document was found with `documentId`.",
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: _base_500_response(),
        },
        examples=[example_document, example_error],
    ),
    "destroy": extend_schema(
        summary="Remove an existing document and its attachments",
        description="Permission to access the document is checked as follows:\n"
        "* Authenticated users are allowed access to the document if they are the owner of the document.\n\n"
        # TODO: Uncomment when organization features are implemented
        # "or the document is owned by an organization and the user has permission to act "
        # "on behalf of that organization.\n\n"
        "The following rules apply:\n"
        "* Drafts may be removed by the owning user.",
        # TODO: Uncomment when organization features are implemented
        # "or an organization's representative, "
        # "if the document is owned by an organization. This is possible even if the `lockedAfter` date has passed, "
        # "to enable a user to remove expired applications.",
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description="The specified Document and its attachments were removed successfully",
            ),
            (status.HTTP_400_BAD_REQUEST, "application/json"): _base_400_response(),
            status.HTTP_401_UNAUTHORIZED: _base_401_response(),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description="The authenticated user lacks the proper permissions to access the document. "
                "Depending on the requested document, "
                "either the user does not belong to the admin group of the service which owns the document, "
                "the user does not own the document."
                # TODO: Uncomment when organization features are implemented
                # " or the user does not have permission to act on behalf "
                # "of the organization which owns the document."
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="No document was found with `documentId`.",
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: _base_500_response(),
        },
        examples=[example_error],
    ),
    # Not implementing
    "update": extend_schema(exclude=True),
}

document_metadata_viewset_docs = {
    "retrieve": extend_schema(
        summary="List and filter non sensitive parts of users documents.",
        description="""List users documents parts that doesn't contain sensitive information to easily see current
        applications and documents of a single user across services.""",
        # "of that organization.",
        responses={
            (status.HTTP_200_OK, "application/json"): OpenApiResponse(
                response=DocumentMetadataSerializer,
                description="User was found and their documents are listed.",
            ),
            (status.HTTP_400_BAD_REQUEST, "application/json"): _base_400_response(),
            status.HTTP_401_UNAUTHORIZED: _base_401_response(),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Current authentication doesn't allow viewing of this users documents"
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="No user matches the given query.",
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: _base_500_response(),
        },
        examples=[example_document_metadata, example_error],
        parameters=[
            OpenApiParameter(
                "status",
                OpenApiTypes.STR,
                description="Search for documents with the given status",
            ),
            OpenApiParameter(
                "type",
                OpenApiTypes.STR,
                description="Search for documents with the given type",
            ),
            OpenApiParameter(
                "transaction_id",
                OpenApiTypes.STR,
                description="Search for documents with the given transaction id",
            ),
        ],
    ),
    # Not implementing
    "list": extend_schema(exclude=True),
    "update": extend_schema(exclude=True),
    "partial_update": extend_schema(exclude=True),
    "destroy": extend_schema(exclude=True),
    "create": extend_schema(exclude=True),
}

document_gdpr_viewset = {
    "retrieve": extend_schema(
        examples=[example_gdpr_api_repsonse],
        description="Used to fetch GDPR data of an user from single service.",
        summary="List user's document details and number of deletable and undeletable documents.",
        responses={
            (status.HTTP_200_OK, "application/json"): OpenApiResponse(
                response=GDPRSerializer,
                description="User was found and their documents are listed."
                " Number of deletable and undeletable documents are included.",
            ),
            (status.HTTP_400_BAD_REQUEST, "application/json"): _base_400_response(),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description="Authorization not provided. API Key authentication required."
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Current authentication doesn't allow viewing of this users documents"
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: _base_500_response(),
        },
    ),
    "destroy": extend_schema(
        examples=[example_gdpr_api_repsonse],
        description="Delete user's documents from a single service that aren't under contractual obligation.",
        summary="List user's documents that weren't deleted. Deletable field should be zero.",
        responses={
            (status.HTTP_200_OK, "application/json"): OpenApiResponse(
                response=GDPRSerializer,
                description="User was found and their deletable documents and attachments have been removed. "
                "Documents with contractual oblications are returned in response body."
                " Field 'total_deletable' should now be zero.",
            ),
            (status.HTTP_400_BAD_REQUEST, "application/json"): _base_400_response(),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description="Authorization not provided. API Key authentication required."
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Current authentication doesn't allow viewing of this users documents"
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: _base_500_response(),
        },
    ),
    # Not implementing
    "list": extend_schema(exclude=True),
    "update": extend_schema(exclude=True),
    "partial_update": extend_schema(exclude=True),
    "create": extend_schema(exclude=True),
}

document_statistics_viewset_docs = {
    "list": extend_schema(
        summary="List and filter non sensitive parts of service's documents.",
        description="""Lists non sensitive data of all documents in ATV. Service staff can fetch data from the
         respective service. Currently the use case is to verify documents match between ATV and services.""",
        responses={
            (status.HTTP_200_OK, "application/json"): OpenApiResponse(
                response=DocumentMetadataSerializer,
                description="Request was allowed and documents were listed",
            ),
            (status.HTTP_400_BAD_REQUEST, "application/json"): _base_400_response(),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                "Request's credentials are missing or invalid. An API-key is required, or an "
                "user token associated with statistics service.",
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Current authentication doesn't allow viewing document statistics"
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: _base_500_response(),
        },
        examples=[example_statistics_data, example_error],
        parameters=[
            OpenApiParameter(
                "statuses",
                OpenApiTypes.STR,
                description="Search for documents with the given statuses separated by comma.",
            ),
            OpenApiParameter(
                "types",
                OpenApiTypes.STR,
                description="Search for documents with the given types separated by comma",
            ),
            OpenApiParameter(
                "services",
                OpenApiTypes.STR,
                description="Search for documents with the given services separated by comma",
            ),
            OpenApiParameter(
                "transaction_id",
                OpenApiTypes.STR,
                description="Search for documents with the given transaction id",
            ),
        ],
    ),
    # Not implementing
    "retrieve": extend_schema(exclude=True),
    "update": extend_schema(exclude=True),
    "partial_update": extend_schema(exclude=True),
    "destroy": extend_schema(exclude=True),
    "create": extend_schema(exclude=True),
}

document_status_history_viewset_docs = {
    "list": extend_schema(
        summary="Lists document's status and activity history",
        description="""Lists all document's statuses and activities related to the statuses""",
        responses={
            (status.HTTP_200_OK, "application/json"): OpenApiResponse(
                response=StatusHistorySerializer,
                description="Request was allowed and document statuses were listed",
            ),
            (status.HTTP_400_BAD_REQUEST, "application/json"): _base_400_response(),
            status.HTTP_401_UNAUTHORIZED: "Request's credentials are missing or invalid.",
            status.HTTP_500_INTERNAL_SERVER_ERROR: _base_500_response(),
        },
        examples=[example_get_status_activity_data, example_error],
    ),
    "create": extend_schema(
        summary="Create new status and/or activity for document",
        description="Allows creating either individual new status, activity or both status and activity. See example",
        request=CreateStatusHistorySerializer,
        responses={
            (status.HTTP_201_CREATED, "application/json"): OpenApiResponse(
                response=StatusHistorySerializer,
                description="New Status and/or Activity was created. All Activities related to the status is returned.",
            ),
            (status.HTTP_200_OK, "application/json"): OpenApiResponse(
                response=StatusHistorySerializer,
                description="""Return HTTP 200 OK, if nothing changed but request was correctly formated.
                 For example if same status is posted twice. Returns latest StatusHistory object.""",
            ),
            (status.HTTP_400_BAD_REQUEST, "application/json"): _base_400_response(),
            status.HTTP_401_UNAUTHORIZED: "Request's credentials are missing or invalid.",
            status.HTTP_500_INTERNAL_SERVER_ERROR: _base_500_response(),
        },
        examples=[example_create_status_activity_data],
    ),
    "retrieve": extend_schema(exclude=True),
    "update": extend_schema(exclude=True),
    "partial_update": extend_schema(exclude=True),
    "destroy": extend_schema(exclude=True),
}
