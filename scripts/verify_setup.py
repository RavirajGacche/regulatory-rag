"""Proves every piece of infrastructure works.  uv run python scripts/verify_setup.py"""

import sys
import time

sys.path.insert(0, ".")
from shared.config import settings

results = {}
SENTENCES = [
    "RBI issued new KYC guidelines for NBFCs",
    "The Reserve Bank published updated know-your-customer rules",
    "Postgres uses B-tree indexes for range queries",
]


def step(n, title):
    print(f"\n{'-' * 60}\nSTEP {n} - {title}\n{'-' * 60}")


def check_postgres():
    step(1, "Postgres + pgvector")
    try:
        from sqlalchemy import create_engine, text

        eng = create_engine(settings.postgres_url)
        with eng.connect() as c:
            print("  ok ", c.execute(text("SELECT version()")).scalar().split(",")[0])
            ext = c.execute(text("SELECT extversion FROM pg_extension WHERE extname='vector'")).scalar()
            if not ext:
                print("  FAIL pgvector missing -> docker compose down -v && docker compose up -d")
                return False
            print("  ok  pgvector", ext)
        return True
    except Exception as e:
        print("  FAIL", type(e).__name__, e)
        return False


def check_mongo():
    step(2, "MongoDB")
    try:
        from pymongo import MongoClient

        cl = MongoClient(settings.mongo_url, serverSelectionTimeoutMS=3000)
        print("  ok  MongoDB", cl.server_info()["version"])
        col = cl[settings.mongo_db].raw_documents
        col.insert_one({"_verify": True, "source": "RBI"})
        print("  ok  wrote", col.count_documents({"_verify": True}), "doc")
        col.delete_many({"_verify": True})
        return True
    except Exception as e:
        print("  FAIL", type(e).__name__, e)
        return False


def check_redis():
    step(3, "Redis")
    try:
        import redis

        r = redis.from_url(settings.redis_url, decode_responses=True)
        r.ping()
        r.setex("_v", 10, "hi")
        print("  ok  setex ->", r.get("_v"), "ttl", r.ttl("_v"))
        r.delete("_v")
        return True
    except Exception as e:
        print("  FAIL", type(e).__name__, e)
        return False


def check_embeddings():
    step(4, "Embeddings")
    try:
        from sentence_transformers import SentenceTransformer

        t = time.time()
        m = SentenceTransformer(settings.embedding_model)
        print(f"  ok  model loaded in {time.time() - t:.1f}s")
        v = m.encode(SENTENCES, normalize_embeddings=True)
        print("  ok  shape", v.shape)
        sim = v @ v.T
        print(f"  KYC vs KYC-paraphrase : {sim[0][1]:.3f}  (high = semantic match)")
        print(f"  KYC vs Postgres       : {sim[0][2]:.3f}  (low = unrelated)")
        return m, v
    except Exception as e:
        print("  FAIL", type(e).__name__, e)
        return None, None


def check_vector_search(m, v):
    step(5, "Vector store + search in Postgres")
    if m is None:
        print("  skip (no embeddings)")
        return False
    try:
        from sqlalchemy import create_engine, text

        eng = create_engine(settings.postgres_url)
        with eng.connect() as c:
            c.execute(text("DROP TABLE IF EXISTS _vt"))
            c.execute(text(f"CREATE TABLE _vt (label TEXT, emb vector({settings.embedding_dim}))"))
            for s, e in zip(SENTENCES, v, strict=True):
                c.execute(text("INSERT INTO _vt VALUES (:l, :e)"), {"l": s, "e": str(e.tolist())})
            q = m.encode("What are the customer verification rules?", normalize_embeddings=True)
            rows = c.execute(
                text("SELECT label, 1 - (emb <=> :q) FROM _vt ORDER BY emb <=> :q LIMIT 3"),
                {"q": str(q.tolist())},
            ).fetchall()
            print("  QUERY: 'What are the customer verification rules?'")
            for i, (lbl, s) in enumerate(rows, 1):
                print(f"   {i}. {s:.3f}  {lbl}")
            c.execute(text("DROP TABLE _vt"))
            c.commit()
        return True
    except Exception as e:
        print("  FAIL", type(e).__name__, e)
        return False


def check_llm():
    step(6, "LLM (Groq)")
    if not settings.groq_api_key:
        print("  FAIL GROQ_API_KEY empty in .env")
        return False
    try:
        from groq import Groq

        t = time.time()
        r = Groq(api_key=settings.groq_api_key.get_secret_value()).chat.completions.create(
            model=settings.groq_model,
            messages=[{"role": "user", "content": "Reply with exactly: SETUP OK"}],
            max_tokens=10,
        )
        print(f"  ok  {r.choices[0].message.content.strip()!r} in {(time.time() - t) * 1000:.0f}ms")
        return True
    except Exception as e:
        print("  FAIL", type(e).__name__, e)
        return False


if __name__ == "__main__":
    results["Postgres"] = check_postgres()
    results["Mongo"] = check_mongo()
    results["Redis"] = check_redis()
    model, vecs = check_embeddings()
    results["Embeddings"] = model is not None
    results["Vector search"] = check_vector_search(model, vecs)
    results["LLM"] = check_llm()
    print("\n" + "=" * 60)
    for k, ok in results.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {k}")
    print("=" * 60)
    sys.exit(0 if all(results.values()) else 1)
