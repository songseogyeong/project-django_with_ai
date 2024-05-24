## 🖥️ AI 서비스 상용화 프로젝트

#### 대상 프로젝트

> 청년들의 문화생활 플랫폼 '틴플레이(Teenplay)'  
> Git-hub: https://github.com/hyuncoding/teenplay_server  
> Website: http://teenplay.site

#### AI 서비스

> 회원별 활동 추천 서비스

### 📌 목차

1. 데이터 수집
   1) 모임 데이터
   2) 활동 데이터
2. 데이터 탐색 및 정제
   1) 모임 데이터
   2) 활동 데이터
3. 데이터 전처리
4. 사전 모델 학습
5. 사전 모델 평가
6. 회원별 모델 추가 학습
7. Django 프로젝트 상용화
8. 트러블슈팅 및 느낀 점

---

### 1. 데이터 수집

#### 1) 모임 데이터

-   데이터 수집 사이트: https://m.blog.naver.com/so_moim?tab=1
-   `selenium` 라이브러리를 통한 크롤링으로 데이터를 수집하였습니다.
-   크롤링 목적은 '활동' 데이터 수집에 앞서, 각 활동을 개설한 '모임' 데이터 수집을 위한 모임 이름 더미 데이터 수집입니다.
-   <details>
        <summary>Click to see full code</summary>

            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            import csv
            import time
            from tqdm import tqdm
            
            with open('scraped_data2.csv', 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file, quoting=csv.QUOTE_NONE)  # CSV 파일에 쓰기 위한 writer 객체 생성
                writer.writerow(['club_title'])  # CSV 헤더 작성
                # ChromeDriver 설정
                service = Service(ChromeDriverManager().install())
                options = Options()
                options.add_argument('--headless')  # 브라우저를 백그라운드에서 실행
                driver = webdriver.Chrome(service=service, options=options)
            
                # 웹사이트 열기
                driver.get("https://m.blog.naver.com/so_moim?tab=1")
            
                # 잠시 대기
                driver.implicitly_wait(10)
            
                # 페이지 끝까지 스크롤 다운하여 콘텐츠 로드
                SCROLL_PAUSE_TIME = 2
            
                last_height = driver.execute_script("return document.body.scrollHeight")
            
                title_set = set()
            
                for i in tqdm(range(50)):
                    # 페이지 끝까지 스크롤 다운
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
                    # 새로운 콘텐츠가 로드될 때까지 대기
                    time.sleep(SCROLL_PAUSE_TIME)
            
                    # 새로운 스크롤 높이 계산
                    new_height = driver.execute_script("return document.body.scrollHeight")
            
                    # 더 이상 새로운 콘텐츠가 없으면 루프 종료
                    if new_height == last_height:
                        break
            
                    last_height = new_height
            
                # 제목 텍스트들 찾기
                titles = driver.find_elements(By.CSS_SELECTOR, ".title__UUn4H span")  # "title-class-name"을 실제 클래스 이름으로 변경
            
                # 제목 텍스트 출력
                for title in tqdm(titles):
                    title = title.text
                    if "<" in title and ">" in title:
                        title = title.split("<")[-1]
                        if title[-1] != ">":
                            target_idx = title.index(">")
                            title = title[:target_idx]
                        else:
                            title = title[:-1]
                    else:
                        continue
                    title = title.replace('"', "")
                    title = title.replace(',', '')
                    if title not in title_set:
                        writer.writerow([title])
                        title_set.add(title)
            
                # 브라우저 종료
                driver.quit()

   </details>

![club_original_data_csv](https://github.com/hyuncoding/django_with_ai/assets/134760674/a269c261-2624-479d-9ae0-3db8bb9501dd)

#### 2) 활동 데이터

- 데이터 수집 사이트
   - https://www.ppomppu.co.kr/zboard/zboard.php?id=experience
   - https://kmong.com/category/24001
   - https://www.frip.co.kr/category/beauty/all?page=2
   - https://meta-chehumdan.com/campaign_list.php?category_id=001A

### 2. 데이터 탐색 및 정제

#### 1) 모임 데이터

- 크롤링으로 수집한 모임 이름(club_title) 데이터에 대해, 데이터베이스의 컬럼명과 일치할 수 있도록 컬럼명을 바꿔주었습니다.

- <details>
    <summary>Click to see full code</summary>

        c_df = c_df.rename(columns={'club_title': 'club_name'})
        c_df

</details>

![club_rename](https://github.com/hyuncoding/django_with_ai/assets/134760674/1be13d35-434a-4152-a821-88a5e06ca5e0)

- 데이터베이스에 INSERT하기 위해 필요한 컬럼들을 추가하였습니다.
- 대표 카테고리의 경우 모임의 종류에 맞는 카테고리의 id를 직접 넣어주었습니다.
- 지역의 경우 `random.randint()`을 통해 지역 id를 무작위로 넣었습니다.
- 카테고리id에 맞는 카테고리명을 '모임 소개(club_intro)'와 '모임 정보(club_info)'에 입력하였습니다.
- '상태(status)'의 경우 1(True)을 입력하였습니다.
- '모임장 id(member_id)'의 경우 데이터베이스에 존재하는 회원의 id중 1개를 무작위로 입력하였습니다.
- '생성일(created_date)'과 '수정일(updated_date)'은 2024년 1월 1일과 현재 날짜 사이의 날짜를 임의로 넣었으며, 수정일이 생성일보다 앞서지 않도록 조건을 추가하였습니다.
- '모임 프로필 사진(club_profile_path)'과 '모임 배너 사진(club_banner_path)'에는 데이터베이스 테이블 INSERT 시 null이 허용되지 않으므로,  
  공백(' ')으로 넣어주었습니다.

- <details>
    <summary>Click to see full code</summary>

        import random
        import numpy as np
        from datetime import datetime, timedelta

        regions = ['서울', '경기', '인천', '부산', '울산' '경남', '대구', '경북', '충청', '대전', '세종', '전라', '광주', '강원', '제주']
        
        c_df['club_region_id'] = c_df['club_region_id'].apply(lambda x: random.randint(1, 15))
        
        categories = ['취미', '문화·예술', '운동·액티비티', '푸드·드링크', 
                          '여행·동행', '성장·자기개발', '동네·또래', '연애·소개팅',
                          '재테크', '외국어', '스터디', '지역축제', '기타']
        
        # 카테고리 id에 따른 카테고리 이름을 매핑하는 딕셔너리
        category_dict = {i+1: categories[i] for i in range(13)}
        
        
        intro_templates = [
            "{club_name}는 {category_name}에 관심이 많은 분들을 위한 모임입니다.",
            "{club_name}는 {category_name}을(를) 함께 즐기고 배우는 모임입니다.",
            "이 모임, {club_name}는 {category_name}에 흥미를 가진 분들이 모이는 곳입니다.",
            "{category_name}을(를) 좋아하는 사람들이 모인 {club_name}에 오신 것을 환영합니다.",
            "{club_name}는 {category_name} 관련 다양한 활동을 함께하는 모임입니다."
        ]
        
        # 다양한 정보 문구 리스트
        info_templates = [
            "{club_name} 모임은 {category_name}에 대한 열정을 가진 사람들이 모이는 곳입니다.",
            "{club_name} 모임에서는 {category_name}에 관한 다양한 주제로 활동을 합니다.",
            "{category_name}을(를) 좋아하는 사람들과 함께하는 {club_name} 모임입니다.",
            "{category_name} 관련 정보를 교환하고 함께 성장하는 {club_name} 모임입니다.",
            "{club_name} 모임은 {category_name}에 관심 있는 분들을 위한 다양한 프로그램을 제공합니다."
        ]
        
        # 'club_intro'와 'club_info' 컬럼 생성
        c_df['club_intro'] = c_df.apply(lambda row: random.choice(intro_templates).format(club_name=row['club_name'], category_name=category_dict[row['club_main_category_id']]), axis=1)
        c_df['club_info'] = c_df.apply(lambda row: random.choice(info_templates).format(club_name=row['club_name'], category_name=category_dict[row['club_main_category_id']]), axis=1)
        
        c_df['status'] = 1
        
        member_ids = [i for i in range(2, 10019)]
        c_df['member_id'] = c_df['member_id'].apply(lambda x: random.choice(member_ids))
        
        # 랜덤 날짜 생성 함수
        def random_date(start, end):
            return start + timedelta(
                seconds=random.randint(0, int((end - start).total_seconds())),
            )
        
        # 현재 시간 및 범위 설정
        now = datetime(2024, 5, 19, 4, 23)
        start = datetime(2024, 1, 1, 12, 0)
        
        # 'created_date'와 'updated_date' 컬럼 생성
        created_dates = [random_date(start, now) for _ in range(len(c_df))]
        updated_dates = [random_date(created_date, now) for created_date in created_dates]
        
        c_df['created_date'] = [date.strftime('%Y-%m-%d %H:%M:%S') for date in created_dates]
        c_df['updated_date'] = [date.strftime('%Y-%m-%d %H:%M:%S') for date in updated_dates]

        c_df['club_profile_path'] = ' '
        c_df['club_banner_path'] = ' '

        c_df.to_csv('./datasets/club_data.csv', index=False)

</details>

- csv로 내보낸 파일을 데이터베이스로 IMPORT 한 후, 모임마다 대표 카테고리를 제외한 나머지 카테고리 중 1~3개를 무작위로 골라 데이터프레임으로 생성하였습니다.
- 해당 데이터를 입력할 데이터베이스 테이블의 컬럼에 맞도록 조정하였습니다.
- '생성일(created_date)'과 '수정일(updated_date)'은 모임 데이터와 동일한 방식으로 생성하였습니다.

- <details>
    <summary>Click to see full code</summary>

        import pandas as pd
        import random
        from datetime import datetime, timedelta
        
        # 현재 시간 및 범위 설정
        now = datetime(2024, 5, 19, 4, 23)
        start = datetime(2024, 1, 1, 12, 0)
        
        # 랜덤 날짜 생성 함수
        def random_date(start, end):
            return start + timedelta(
                seconds=random.randint(0, int((end - start).total_seconds()))
            )
        
        # tbl_club_category 데이터프레임 생성
        club_category_data = []
        
        created_dates = [random_date(start, now) for _ in range(len(c_df))]
        updated_dates = [random_date(created_date, now) for created_date in created_dates]
        
        for _, row in c_df.iterrows():
            club_id = row['id']
            main_category_id = row['club_main_category_id']
            
            # 대표 카테고리를 제외한 1~13의 카테고리 중 랜덤 선택 (1~3개)
            category_ids = [i for i in range(1, 14) if i != main_category_id]
            chosen_categories = random.sample(category_ids, random.randint(1, 3))
           
            for category_id in chosen_categories:
                created_date = random_date(start, now)
                updated_date = random_date(created_date, now).strftime('%Y-%m-%d %H:%M:%S')
                club_category_data.append({
                    'created_date': created_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_date': updated_date,
                    'status': 1,  
                    'category_id': category_id,
                    'club_id': club_id
                })
        
        # 데이터프레임으로 변환
        club_category_df = pd.DataFrame(club_category_data)
        
        # CSV 파일로 저장
        club_category_df.to_csv('./datasets/tbl_club_category.csv', index=False)

        club_category_df

  </details>

![club_category](https://github.com/hyuncoding/django_with_ai/assets/134760674/6cf6e333-05f9-4a0f-a504-e05203cd05ec)

#### 2) 활동 데이터

- 크롤링으로 수집한 활동 데이터에 대해, 카테고리에 맞는 카테고리id를 직접 입력해주었습니다.
- 또한 '활동 내용(activity_content)'과 '활동 소개(activity_intro)'를 제목에 맞게 입력해주었습니다.
  
![activity_original_data_csv](https://github.com/hyuncoding/django_with_ai/assets/134760674/c49d607e-5e79-4e70-aa89-51b6a79f05c0)

- 활동 개설 시, 원래대로라면 결제id가 필요하므로 이미 존재하는 결제 데이터의 id를 랜덤으로 넣어주었습니다.

- <details>
    <summary>Click to see full code</summary>

      pay_ids = [i for i in range(1, 75)]
      def get_club_id_by_random(category_id):
          club_ids = club_df.loc[club_df['club_main_category_id'] == category_id, 'id']
          club_id = random.sample(sorted(club_ids), 1)[0]
          return club_id
      
      a_df['pay_id'] = 0
      a_df['pay_id'] = a_df['pay_id'].apply(lambda x: random.sample(pay_ids, 1)[0])
      a_df

  </details>

![activity_with_payid](https://github.com/hyuncoding/django_with_ai/assets/134760674/1e4fd550-cf22-4494-b834-ce0af4ab4209)

- 이후 활동의 카테고리와 일치하는 대표 카테고리를 가진 모임의 id를 랜덤으로 넣어주었습니다.
- '상태(status)'는 1(True)로 입력하였습니다.
- '활동 썸네일(thumbnail_path)'과 '활동 배너(banner_path)'는 공백(' ')으로 입력하였습니다.
- '활동 장소(activity_address_location)'는 개설한 모임의 장소를 입력한 후, 활동 제목이나 내용에 제목이 있을 경우 비교하여 일치하도록 조정하였습니다.
- '활동 장소 설명(activity_address_detail)'은 임의로 '주차 공간 없습니다.'로 입력하였습니다.
- '생성일(created_date)'과 '수정일(updated_date)'은 모임 데이터와 동일한 방식으로 입력하였으며,  
  '모집 시작일(recruit_start)'과 '모집 종료일(recruit_end)', '활동 시작일(activity_start)' 및 '활동 종료일(activity_end)' 또한
  같은 방식으로 입력하였습니다.
  
- <details>
    <summary>Click to see full code</summary>

      a_df['club_id'] = a_df['category_id'].apply(lambda x: get_club_id_by_random(x))
      a_df['status'] = 1
      a_df['thumbnail_path'] = ' '
      a_df['banner_path'] = ' '
      a_df['activity_address_detail'] = '주차 공간 없습니다.'
  
      # 현재 시간 및 범위 설정
      now = datetime(2024, 5, 19, 4, 23)
      start = datetime(2024, 1, 1, 12, 0)
      
      # 'created_date'와 'updated_date' 컬럼 생성
      created_dates = [random_date(start, now) for _ in range(len(a_df))]
      updated_dates = [random_date(created_date, now) for created_date in created_dates]
      recruit_starts = [random_date(created_date, now) for created_date in created_dates]
      recruit_ends = [random_date(recruit_start, now) for recruit_start in recruit_starts]
      activity_starts = [random_date(recruit_end, now) for recruit_end in recruit_ends]
      activity_ends = [random_date(activity_start, now) for activity_start in activity_starts]
      
      
      a_df['created_date'] = [date.strftime('%Y-%m-%d %H:%M:%S') for date in created_dates]
      a_df['updated_date'] = [date.strftime('%Y-%m-%d %H:%M:%S') for date in updated_dates]
      a_df['recruit_start'] = [date.strftime('%Y-%m-%d %H:%M:%S') for date in recruit_starts]
      a_df['recruit_end'] = [date.strftime('%Y-%m-%d %H:%M:%S') for date in recruit_ends]
      a_df['activity_start'] = [date.strftime('%Y-%m-%d %H:%M:%S') for date in activity_starts]
      a_df['activity_end'] = [date.strftime('%Y-%m-%d %H:%M:%S') for date in activity_ends]
      a_df.to_csv('./datasets/activity_lists.csv', index=False)

  </details>

### 3. 데이터 전처리

- 데이터베이스로부터 전체 활동 데이터를 csv파일로 내보낸 후, `Jupyter Notebook` 환경에서 `pandas` 라이브러리를 통해 불러옵니다.
  
- <details>
    <summary>Click to see full code</summary>

        import pandas as pd

        a_df = pd.read_csv('./datasets/tbl_activity.csv', low_memory=False)
        a_df
    
  </details>

![tbl_activity](https://github.com/hyuncoding/django_with_ai/assets/134760674/7d696285-0780-45f9-a82f-d4529f0a7ca4)

- 모델 학습 대상 컬럼들을 추출하여 새로운 데이터프레임으로 구성합니다.

- <details>
    <summary>Click to see full code</summary>

        pre_a_df = a_df[['activity_title', 'activity_content', 'activity_intro', 'activity_address_location', 'category_id']]
        pre_a_df

  </details>

![pre_a_df](https://github.com/hyuncoding/django_with_ai/assets/134760674/028925d5-d6a7-4b52-be57-63cc5590cd5d)

- 'category_id(활동 카테고리의 id)'를 예측 타겟으로, 나머지 컬럼을 feature로 설정하였습니다.
- 크롤링을 통해 수집한 데이터가 아닌 원래 데이터의 경우, `summernote` API를 통해 작성한 내용이 포함되어 있으므로,  
  `<p></p>`와 같은 html 태그들이 존재하였습니다.
- 따라서 정규표현식을 사용하여 해당 부분을 빈 문자열로 대체합니다.
  
- <details>
    <summary>Click to see full code</summary>

        import re
        def remove_html_tags(text):
            # 정규표현식을 사용하여 HTML 태그를 찾습니다.
            clean = re.compile('<.*?>')
            # 태그를 빈 문자열로 대체합니다.
            return re.sub(clean, '', text)

        pre_a_df.activity_content = pre_a_df.activity_content.apply(remove_html_tags)

  </details>

- 또한 `"`(큰따옴표)를 제거합니다.

- <details>
    <summary>Click to see full code</summary>

        pre_a_df.activity_content = pre_a_df.activity_content.apply(lambda x: x.replace("\"", ""))

  </details>

![replaced_pre_a_df](https://github.com/hyuncoding/django_with_ai/assets/134760674/8525d4cd-c72c-4969-bb94-2c1b2c0957d1)

- feature로 설정한 4개의 컬럼을 하나의 문장으로 합친 후, 'feature' 컬럼을 만들고 저장합니다.
  
- <details>
    <summary>Click to see full code</summary>

        def get_full_feature(df):
            result = []
            columns = df.columns[:-1]
            for i in range(len(df)):
                text = ''
                for column in columns:
                    now = df.iloc[i][column]
                    if str(now) == 'nan' or not now:
                        continue
                    text += str(now) + ' '
                result.append(text)
            return result
                
        result = get_full_feature(pre_a_df)
        pre_a_df['feature'] = result

  </details>

![combined_features](https://github.com/hyuncoding/django_with_ai/assets/134760674/18c009e8-7743-47d7-a9a4-f3d7408685c9)

- 결합한 문장에서, 숫자, 알파벳 및 한글을 제외한 특수문자를 제거합니다.
- 제거한 feature와 target(category_id)로 구성된 새로운 데이터프레임을 생성합니다.

- <details>
    <summary>Click to see full code</summary>

        def remove_special_characters_except_spaces(text):
            """
            주어진 텍스트에서 숫자, 한글, 영어 알파벳을 제외한 모든 특수문자 및 기호를 제거하고,
            공백은 유지합니다.
        
            :param text: 특수문자 및 기호를 포함한 문자열
            :return: 특수문자 및 기호가 제거된 문자열 (공백 유지)
            """
            # 정규표현식을 사용하여 숫자, 한글, 영어 알파벳, 공백을 제외한 모든 문자를 찾습니다.
            clean = re.compile('[^0-9a-zA-Zㄱ-ㅎ가-힣ㅏ-ㅣ ]')
            # 특수문자 및 기호를 빈 문자열로 대체합니다.
            return re.sub(clean, ' ', text)

        pre_a_df.feature = pre_a_df.feature.apply(remove_special_characters_except_spaces)
        main_df = pre_a_df[['feature', 'category_id']]
  
  </details>

![main_df](https://github.com/hyuncoding/django_with_ai/assets/134760674/c849fc53-e193-47d0-bfbe-a7ee18b50772)

### 4. 사전 모델 학습

> `scikit-learn` 라이브러리를 활용하여 진행합니다.  
> `CountVectorizer()`을 통해 벡터로 변환된 feature를 `MultinomialNB()` 분류 모델에 전달하여 타겟을 예측합니다.  
> `Pipeline()`을 통해 파이프라인을 구축하여 진행합니다.  

- <details>
    <summary>Click to see full code</summary>

        from sklearn.model_selection import train_test_split
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.naive_bayes import MultinomialNB
        from sklearn.pipeline import Pipeline
        
        count_v = CountVectorizer()
        
        pipe = Pipeline([('count_v', count_v), ('mnnb', MultinomialNB())])
        
        features, targets = main_df['feature'], main_df['category_id']
        
        X_train, X_test, y_train, y_test = train_test_split(features, targets, stratify=targets, test_size=0.2, random_state=124)
        
        pipe.fit(X_train, y_train)

  </details>

- 학습한 모델을 평가하기 위한 함수를 정의합니다.

- <details>
    <summary>Click to see full code</summary>

        import matplotlib.pyplot as plt
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, ConfusionMatrixDisplay
        
        def get_evaluation(y_test, prediction, classifier=None, X_test=None):
            confusion = confusion_matrix(y_test, prediction)
            accuracy = accuracy_score(y_test , prediction)
            precision = precision_score(y_test , prediction, average='macro')
            recall = recall_score(y_test , prediction, average='macro')
            f1 = f1_score(y_test, prediction, average='macro')
            
            print('오차 행렬')
            print(confusion)
            print('정확도: {0:.4f}, 정밀도: {1:.4f}, 재현율: {2:.4f}, F1: {3:.4f}'.format(accuracy, precision, recall, f1))
            print("#" * 80)
            
            if classifier is not None and  X_test is not None:
                fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12,4))
                titles_options = [("Confusion matrix", None), ("Normalized confusion matrix", "true")]
        
                for (title, normalize), ax in zip(titles_options, axes.flatten()):
                    disp = ConfusionMatrixDisplay.from_estimator(classifier, X_test, y_test, ax=ax, cmap=plt.cm.Blues, normalize=normalize)
                    disp.ax_.set_title(title)
                plt.show()

  </details>

### 5. 사전 모델 평가

> 앞서 정의한 평가 함수를 통해, 테스트 데이터(`X_test`)에 대한 예측을 진행한 후 평가합니다.  
> 평가 지표는 정확도(accuracy), 정밀도(precision), 재현율(recall), f1-score 등이며, 오차 행렬을 시각화합니다.  

- <details>
    <summary>Click to see full code</summary>

        prediction = pipe.predict(X_test)
        get_evaluation(y_test, prediction, pipe, X_test)

  </details>

![confusion_matrix](https://github.com/hyuncoding/django_with_ai/assets/134760674/5dbeb6d4-4920-47b3-9c73-b2b607e89cdf)

- 정확도가 약 0.5991, f1-score가 약 0.4817로 저조했지만, 카테고리(타겟)별 분포 비중이 고르지 않기 때문으로 예상되었습니다.

![category_value_counts](https://github.com/hyuncoding/django_with_ai/assets/134760674/1e776966-9b8f-4b4d-a923-7b475327b01e)

- 실제로 데이터 개수가 많은 1번 및 3번 카테고리의 경우 정규화된 오차 행렬을 보았을 때 약 0.87과 0.91로, 매우 높은 정확도를 보이고 있음을 알 수 있습니다.
- 따라서 사전 훈련 모델을 활용하여 회원별 개인 모델을 생성한 후 추가 학습을 진행하였을 때 높은 성능을 기대할 수 있을 것으로 판단됩니다.
- 해당 모델을 `joblib` 라이브러리를 통해 `.pkl`파일로 내보냅니다.

- <details>
    <summary>Click to see full code</summary>

        import pickle
        import joblib
        
        joblib.dump(pipe, './activity_recommender.pkl')

  </details>

### 6. 회원별 모델 추가 학습

> 회원가입 시 자동으로 회원별 활동 추천 모델을 생성합니다.  
> 해당 모델은 먼저 사전 훈련 모델을 기준으로 복사되며,  
> 회원이 1) 활동 상세페이지 접속 시, 2) 관심 활동 등록 시 추가 학습을 진행합니다.  

- 활동 상세페이지 이동 및 관심 활동 등록 시 모두, 같은 방식으로 추가 학습을 진행합니다.
- 해당 활동의 카테고리 이름과 활동 제목, 활동 소개 및 활동 장소를 하나의 문장으로 합친 후,  
  불러온 파이프라인 모델의 `CountVectorizer()`에 전달하여 벡터화합니다.  
- 벡터화된 값을 파이프라인 모델의 `MultinomialNB()`에 전달하여 `partial_fit()`을 통해 추가 학습을 진행합니다.
- 이때 정답 라벨(y)은 해당 활동의 카테고리 id로 설정합니다.
  
- 활동 상세 페이지에 대한 get 요청에 응답하는 Django View인 ActivityDetailWebView의 get() 메소드 중, 추가 학습 관련 코드입니다.

- <details>
    <summary>Click to see full code</summary>

        # 활동 상세페이지는 기획 상 로그인한 유저만 조회할 수 있으므로 세션에서 사용자의 id를 받아와 저장합니다.
        member_id = request.session['member']['id']
        member = Member.enabled_objects.get(id=member_id)

        # 회원에 맞는 활동 추천 ai 모델을 불러옵니다.
        model_file_name = member.member_recommended_activity_model

        # path
        model_file_path = os.path.join(Path(__file__).resolve().parent.parent, model_file_name)

        # pkl 파일을 열어 객체 로드
        model = joblib.load(model_file_path)

        # 불러온 ai 모델에 추가 fit을 진행합니다.
        additional_X_train = [activity.category.category_name + activity.activity_title + activity.activity_intro + activity.activity_address_location]
        additional_y_train = [activity.category.id]

        additional_X_train_transformed = model.named_steps['count_v'].transform(additional_X_train)
        model.named_steps['mnnb'].partial_fit(additional_X_train_transformed, additional_y_train, classes=[i for i in range(1, 14)])

        # fit이 완료된 모델을 다시 같은 경로에 같은 이름으로 내보내줍니다.
        joblib.dump(model, member.member_recommended_activity_model)

  </details>

- 관심 활동 추가에 대한 REST 방식 get 요청에 응답하는 Django View인 ActivityLikeAPI의 get() 메소드 중, 추가 학습 관련 부분입니다.
  
- <details>
    <summary>Click to see full code</summary>

        member = Member.enabled_objects.get(id=member_id)
        activity = Activity.enabled_objects.get(id=activity_id)

        # 회원에 맞는 활동 추천 ai 모델을 불러옵니다.
        model_file_name = member.member_recommended_activity_model

        # path
        model_file_path = os.path.join(Path(__file__).resolve().parent.parent, model_file_name)

        # pkl 파일을 열어 객체 로드
        model = joblib.load(model_file_path)

        # 불러온 ai 모델에 추가 fit을 진행합니다.
        additional_X_train = [
            activity.category.category_name + activity.activity_title + activity.activity_intro + activity.activity_address_location]
        additional_y_train = [activity.category.id]

        additional_X_train_transformed = model.named_steps['count_v'].transform(additional_X_train)
        model.named_steps['mnnb'].partial_fit(additional_X_train_transformed, additional_y_train,
                                              classes=[i for i in range(1, 14)])

        # fit이 완료된 모델을 다시 같은 경로에 같은 이름으로 내보내줍니다.
        joblib.dump(model, member.member_recommended_activity_model)
  
  </details>

### 7. Django 프로젝트 상용화

> 메인페이지의 'AI 추천 활동' 탭에서 표시합니다.

- 로그아웃 시 현재 시즌에 맞게 기획한 키워드로 예측을 수행합니다.  
- 이때 키워드는 **여행 바다 산 여름 시원한**으로 설정하였습니다.
- 예측된 확률에 따라 상위 2개 카테고리에 대하여, 1위 카테고리의 활동 중 최신순으로 6개를 불러옵니다.
- 마찬가지로 2위 카테고리의 활동 중 최신순으로 2개를 불러옵니다.

#### 🖥️ 로그아웃 시 화면 (사전 훈련 모델 사용)

![mainpage_activity_ai](https://github.com/hyuncoding/django_with_ai/assets/134760674/495edc8e-7a23-4a15-9c0d-dd9bb8a60fa2)

- 로그인 시 회원별 모델로 예측을 수행합니다.
- 이때 입력값은 마이페이지에서 선택한 '관심 분야'의 카테고리 이름들과,  
  마이페이지에서 입력한 '관심 키워드' 3개로 설정하였습니다.
- 마찬가지로 예측된 확률에 따라 상위 2개 카테고리에 대하여 총 8개의 활동을 불러와 표시합니다.
- 아래는 마이페이지의 '관심 분야' 및 '관심 키워드' 선택/입력 화면입니다.

![mypage_interests](https://github.com/hyuncoding/django_with_ai/assets/134760674/e32d5ce6-8db6-4f35-b43c-4e7c1bf71e9d)

#### 🖥️ 로그인 시 화면 (회원별 맞춤 모델 사용)

![mainpage_activity_login_ai](https://github.com/hyuncoding/django_with_ai/assets/134760674/8f03e3d3-2b09-4734-b5f8-0e1427862f2c)

### 8. 트러블슈팅 및 느낀 점

#### 1) `.pkl` 모델 파일 입출력 경로 관련

가. 문제 발생

- `.pkl`파일을 Django의 View에서 불러오는 과정에서 경로 문제가 발생하였습니다.
- 메인 페이지 접속 시 REST 방식으로 받은 추천 활동 리스트 요청에 대해 응답하는 View에서는, 같은 app 폴더 안의 `.pkl` 파일을 불러오는 데 문제가 없었습니다.
- 하지만, 활동 상세 페이지 View나 관심 활동 등록 View의 경우 다른 app 폴더 안에 위치하므로,  
  `.pkl` 파일을 불러오지 못했습니다.

나 원인 추론

- `os.path.join()`과 `Path(__file__).resolve().parent` 등의 코드를 작성하며 절대 경로를 잘못 입력한 것으로 예상 후 직접 출력하며 확인해보았으나,  
  `joblib.load()`에 해당 경로를 전달하기 직전에 출력해보았을 때에도 정상적으로 출력되어 다른 원인이 있을 것으로 예상했습니다.
- `joblib.load()`에 경로를 전달하기 직전과, 실제 오류 메시지에서 존재하지 않는 파일 메시지와 함께 출력된 경로에 차이가 존재하였으며,  
  전자와 달리 후자에서는 `/upload/` 경로가 포함되어 있었습니다.
- 회원별 모델 파일의 경로를 저장하는 회원 테이블의 컬럼인 `member_recommended_activity_model` 컬럼이  
  회원 모델 클래스에서 `ImageField()` 타입의 필드로 선언되어 있기 때문으로 파악하였습니다.

다. 해결 방안

- 해당 컬럼의 타입을 변경하기 위해, `member/models.py`에서 `Member` 클래스의 해당 필드를 `TextField()` 타입으로 변경하였습니다.
- 이후 다시 `migration`을 진행하여 데이터베이스에 반영하였습니다.

라. 결과 확인

- 정상적으로 회원별 모델을 저장된 경로에 맞게 불러옴을 확인하였습니다.

#### 2) `.pkl` 모델 추가 학습 진행 관련

가. 문제 발생

- 회원별 `.pkl` 모델 파일을 불러오는 데까지는 문제가 없었으나,  
  추가 학습을 진행할 때 `partial_fit()` 메소드가 파이프라인 객체에서 동작하지 않았습니다.

나. 원인 추론

- 인터넷 검색 및 scikit-learn의 공식 Documentation을 확인한 결과, 파이프라인 모델에 포함된 `CountVectorizer()`의 경우,  
  입력 데이터에 대해 토큰화 및 피처 벡터화를 한 번에 수행하도록 설계되어 `partial_fit()`을 지원하지 않기 때문으로 판단하였습니다.

다. 해결 방안

- 파이프라인 객체의 `named_steps` 를 통해 `CountVectorizer()`와 `MultiNomialNB()`를 각각 가져와 사용하였습니다.
- 이때, `CountVectorizer()`에는 `fit_transform()`이 아닌 `transform()`을 통해 새로운 feature 데이터를 전달하였으며,  
  `MultiNomialNB()`에는 앞서 변환된 feature 데이터를 전달하여 `partial_fit()`으로 추가 학습을 진행하였습니다.

라. 결과 확인

- 활동 상세 페이지 이동 시 및 관심 활동 등록 시 정상적으로 추가 학습이 진행됨을 확인하였습니다.

#### 3) 느낀 점

- 데이터 분석부터 RFM 분석, 머신러닝의 분류(Classification)와 회귀(Regression)를 배우고 다양한 모델을 통해 실습 및 프로젝트를 진행하면서, 다양한 주제의 데이터를 다루어보았지만 실무에서 어떻게 활용할 수 있을지 정확히 알지 못했습니다. 하지만 이번 프로젝트를 통해 데이터로 직접 학습시킨 모델을 실제 웹 서비스에 상용화하며 모델 훈련의 방향성을 직접 정하는 경험을 할 수 있었습니다.
- 또한, 사전 훈련 모델의 예측 결과와 회원별로 추가 학습된 모델의 예측 결과가 실시간으로 달라지는 양상을 확인하며, 모델이 실제로 어떻게 동작하는지, 그리고 회원 맞춤형 추천 시스템이 어떤 방식으로 구축될 수 있는지에 대해 알게 되어 흥미로웠습니다.
- 테스트 데이터에 대한 모델의 정확도가 만족스럽지 않더라도, 회원별 모델이 추가 학습을 거듭함에 따라 회원이 설정한 관심 분야 및 키워드와 관련된 활동을 점점 정확히 예측하는 모습을 보며, 학습/테스트용 사전 데이터에서의 평가 지표만을 신뢰할 수는 없다는 사실을 깨달았습니다. 결국 사전 훈련 모델은 회원별 맞춤 모델을 위한 준비 작업이기 때문에, 평가 지표들에 대해 적절한 합의점을 찾아 실제 예측에서의 성능을 향상시키기 위한 노력이 중요하다는 것 또한 깨달았습니다.



