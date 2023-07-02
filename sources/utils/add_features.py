import os
import numpy as np
import pandas as pd

from PIL import Image
from sources.utils.url_utils import get_image_path_from_url
from sources.classifier import Classifier
from sources.utils.benchmarking import measure_time


def euclidean_distance(embedding1: np.ndarray, embedding2: np.ndarray):
    squared_difference = np.square(embedding1 - embedding2)
    sum_squared_difference = np.sum(squared_difference)
    distance = np.sqrt(sum_squared_difference)

    return distance


def cosine_distance(embedding1: np.ndarray, embedding2: np.ndarray):
    dot_product = np.dot(embedding1, embedding2.T)
    normalised_embedding1 = np.linalg.norm(embedding1)
    normalised_embedding2 = np.linalg.norm(embedding2)
    similarity = dot_product / (normalised_embedding1 * normalised_embedding2)

    return similarity[0][0]


@measure_time
def add_features(dataframe: pd.DataFrame):
    classifier = Classifier()
    processed_dataframe = dataframe.copy()

    for index, row in dataframe.iterrows():
        indexes = []
        embeddings = []

        for url in ["image_url1", "image_url2"]:
            image_path = get_image_path_from_url(row[url])
            if not os.path.exists(image_path):
                embeddings = []
                break
            image = Image.open(image_path)

            logits = classifier(image).detach().numpy()
            score = logits.argmax(-1).item()

            indexes.append(score)
            embeddings.append(logits)

        if not embeddings:
            indexes = [None, None]
            euclidean_similarity = None
            cosine_similarity = None
        else:
            euclidean_similarity = euclidean_distance(embeddings[0], embeddings[1])
            cosine_similarity = cosine_distance(embeddings[0], embeddings[1])

        processed_dataframe.loc[index, 'class_index1'] = indexes[0]
        processed_dataframe.loc[index, 'class_index2'] = indexes[1]
        processed_dataframe.loc[index, 'euclidean_similarity'] = euclidean_similarity
        processed_dataframe.loc[index, 'cosine_similarity'] = cosine_similarity

    return processed_dataframe


def main():
    df = pd.read_csv("../../data/train.csv")
    df = df.head(10)
    df = add_features(df)
    print(df)


if __name__ == "__main__":
    main()