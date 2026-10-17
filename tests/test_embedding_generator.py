
from unittest.mock import MagicMock, patch

import pytest

from src.utils.embedding_generator import generate_embedding


@patch("src.utils.embedding_generator.SentenceTransformer")
def test_generate_embedding_success(mock_model_class):
    mock_model = MagicMock()
    mock_model.encode.return_value = [0.1] * 384
    mock_model_class.return_value = mock_model

    embedding = generate_embedding("Scientific research")

    assert len(embedding) == 384
    assert isinstance(embedding, list)
    mock_model.encode.assert_called_once_with("Scientific research")


@pytest.mark.parametrize("text", ["", "   ", "\n"])
def test_generate_embedding_rejects_empty_text(text):
    with pytest.raises(ValueError, match="Text cannot be empty"):
        generate_embedding(text)
