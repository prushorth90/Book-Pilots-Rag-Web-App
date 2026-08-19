from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

COLLABORATIVE_MODEL = "collaborative.keras"
COLLABORATIVE_METADATA = "collaborative.json"


def train_collaborative_model(
    ratings: list[tuple[int, int, int]], artifact_dir: Path, epochs: int = 20
) -> bool:
    if not ratings:
        return False

    import tensorflow as tf

    user_ids = sorted({user_id for user_id, _, _ in ratings})
    book_ids = sorted({book_id for _, book_id, _ in ratings})
    user_map = {user_id: index for index, user_id in enumerate(user_ids)}
    book_map = {book_id: index for index, book_id in enumerate(book_ids)}

    user_input = tf.keras.Input(shape=(1,), name="user")
    book_input = tf.keras.Input(shape=(1,), name="book")
    user_embedding = tf.keras.layers.Flatten()(
        tf.keras.layers.Embedding(len(user_ids), 32, name="user_embedding")(user_input)
    )
    book_embedding = tf.keras.layers.Flatten()(
        tf.keras.layers.Embedding(len(book_ids), 32, name="book_embedding")(book_input)
    )
    user_bias = tf.keras.layers.Flatten()(
        tf.keras.layers.Embedding(len(user_ids), 1, name="user_bias")(user_input)
    )
    book_bias = tf.keras.layers.Flatten()(
        tf.keras.layers.Embedding(len(book_ids), 1, name="book_bias")(book_input)
    )
    score = tf.keras.layers.Activation("sigmoid")(
        tf.keras.layers.Add()(
            [tf.keras.layers.Dot(axes=1)([user_embedding, book_embedding]), user_bias, book_bias]
        )
    )
    model = tf.keras.Model(inputs=[user_input, book_input], outputs=score)
    model.compile(optimizer=tf.keras.optimizers.Adam(0.01), loss="mse")

    users = np.asarray([user_map[user_id] for user_id, _, _ in ratings], dtype=np.int32)
    books = np.asarray([book_map[book_id] for _, book_id, _ in ratings], dtype=np.int32)
    targets = np.asarray([(rating - 1) / 4 for _, _, rating in ratings], dtype=np.float32)
    model.fit(
        {"user": users, "book": books},
        targets,
        epochs=epochs,
        batch_size=min(64, len(ratings)),
        verbose=0,
    )

    artifact_dir.mkdir(parents=True, exist_ok=True)
    model.save(artifact_dir / COLLABORATIVE_MODEL)
    metadata: dict[str, Any] = {
        "user_map": {str(key): value for key, value in user_map.items()},
        "book_map": {str(key): value for key, value in book_map.items()},
        "rating_count": len(ratings),
    }
    (artifact_dir / COLLABORATIVE_METADATA).write_text(json.dumps(metadata), encoding="utf-8")
    return True
