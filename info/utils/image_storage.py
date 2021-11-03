from qiniu import Auth, put_file, etag, put_data
import qiniu.config


access_key = 'g3pim1LFqP61FODtPzKYklA4ZKe_4eg18Gnyk-jV'
secret_key = 'K2XMez08l77ubTAUSUVxvk1YRbhdVOn9fYDCNRhY'


def image_storage(image_Data):
    q = Auth(access_key, secret_key)

    bucket_name = 'zqinfo'

    key = None

    token = q.upload_token(bucket_name, key, 3600)

    ret, info = put_data(token, key, image_Data)

    #  处理上传的结果
    if info.status_code == 200:
        return ret.get('key')
    else:
        return None


if __name__ == '__main__':
    with open("./photo/0.jpg", 'rb') as f:
        image_storage(f.read())
