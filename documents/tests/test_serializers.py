from documents.serializers import AttachmentSerializer


def test_attachment_serializer_full_uri(rf, attachment):
    request = rf.request()
    assert (
        AttachmentSerializer(attachment, context={"request": request}).data.get("href")
        == f"{request._current_scheme_host}/v1/documents/{attachment.document_id}/attachments/{attachment.id}/"
    )


def test_attachment_serializer_default_uri(attachment):
    assert (
        AttachmentSerializer(attachment).data.get("href")
        == f"/v1/documents/{attachment.document_id}/attachments/{attachment.id}/"
    )
