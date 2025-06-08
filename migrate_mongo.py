from pymongo import MongoClient
import numpy as np
from chromadb import Client, Settings
from datetime import datetime
import os

# .env 파일 로드
load_dotenv()

mongo_url = os.getenv('MONGO_URL')
database_name = os.getenv('DATABASE_NAME')

# MongoDB 연결 설정
client = MongoClient(mongo_url)
db = client[database_name]  # 데이터베이스 선택
collection = db['courses']  # 컬렉션 선택

# Chroma DB 클라이언트 생성
chroma_client = Client(Settings(
    persist_directory='./course_vector_db',
    is_persistent=True
))

# Chroma 컬렉션 가져오기
chroma_collection = chroma_client.get_collection(name="courses")

# 모든 데이터 가져오기
results = chroma_collection.get(include=['embeddings', 'documents', 'metadatas'])

# MongoDB에 데이터 저장
for i in range(len(results['ids'])):
    document = {
        'id': results['ids'][i],
        'content': results['documents'][i],
        'metadata': results['metadatas'][i],
        'embeddings': results['embeddings'][i].tolist(),  # numpy array를 list로 변환
        'created_at': datetime.now()
    }
    print(document)
    
    # upsert=True로 설정하여 이미 존재하는 경우 업데이트
    collection.update_one(
        {'course_id': results['ids'][i]},
        {'$set': document},
        upsert=True
    )

print(f"Successfully stored {len(results['ids'])} documents in MongoDB")

# MongoDB에서 데이터 검색 예시
def find_course_by_id(course_id):
    return collection.find_one({'course_id': course_id})

# 사용 예시
if __name__ == "__main__":
    # 예시로 첫 번째 과정 검색
    sample_id = results['ids'][0]
    found_course = find_course_by_id(sample_id)
    if found_course:
        print(f"\nFound course: {found_course['content']}")
    else:
        print(f"Course not found: {found_course}")