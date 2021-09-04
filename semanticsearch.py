
from sentence_transformers import SentenceTransformer
import scipy.spatial
import pandas as pd
import joblib

embedder = SentenceTransformer('bert-base-nli-mean-tokens')
#corpus = finaldf_sample['text'].values.tolist()
#corpus_embeddings = embedder.encode(corpus)


filename = 'socialmediadata/corpus_embeddings_500.sav'
#joblib.dump(corpus_embeddings, filename)
corpus_embeddings = joblib.load(filename)
#finaldf = pd.read_csv('socialmediadata/twitter_reddit_news_blogs_new.csv')


def get_similar_sentences(finaldf,queries):
    query_embeddings = embedder.encode(queries)

    closest_n = 20
    res=[]
    rows=[]
    for query, query_embedding in zip(queries, query_embeddings):
        distances = scipy.spatial.distance.cdist([query_embedding], corpus_embeddings, "cosine")[0]

        results = zip(range(len(distances)), distances)
        results = sorted(results, key=lambda x: x[1])

        print("\n\n======================\n\n")
        print("Query:", query)
        print("\nTop 5 most similar sentences from similar")

        for idx, distance in results[0:closest_n]:
            #print(meddfr['paper_id'][idx],meddfr['url'][idx],meddfr['url'][idx],meddfr['abstract'][idx], "(Score: %.4f)" % (1-distance))
            res.append([finaldf['id'][idx],finaldf['date'][idx],finaldf['sentiment_score'][idx],finaldf['link'][idx], (1-distance)])
    df = pd.DataFrame(res,columns = ['id','date','sentiment_score','link','Score'])
    print(df)
    return df