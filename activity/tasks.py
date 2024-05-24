import os
from datetime import datetime, timedelta

from django_cron import CronJobBase, Schedule

from activity.models import ActivityImage


class DeleteOldImages(CronJobBase):
    # 매일 밤 12시마다 delete_old_images()를 호출하기 위한 클래스입니다.
    RUN_EVERY_MIDNIGHT = Schedule(run_at_times=['00:00'])

    def do(self):
        delete_old_images()


# 실제로 파일에 접근하여 삭제하는 함수입니다.
def delete_old_images():
    # 현재 시간(매일 밤 자정)을 기준으로 하루 이전 날짜를 구합니다.
    yesterday = datetime.now() - timedelta(days=1)

    # 해당 날짜 이전에 생성된 이미지들 중 status가 0인 이미지들을 tbl_activity_image에서 불러옵니다.
    old_images = ActivityImage.objects.filter(status=0, created_date__lte=yesterday)

    # 각 이미지마다 반복문을 통해 접근합니다.
    for old_image in old_images:
        # 예기치 못한 오류를 방지하기 위해 해당 이미지 객체의 image_path 필드가 None이 아닌지 검사합니다.
        if old_image.image_path:
            # os.remove()에 전달할 이미지 경로를 저장해줍니다.
            image_path = old_image.image_path.path

            # 실제 경로에 해당 파일이 존재할 경우 지워줍니다.
            if os.path.exists(image_path):
                os.remove(image_path)
