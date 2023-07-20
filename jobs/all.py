import time
from baremetal import baremetal
from privatecloud import privatecloud
from publiccloud import publiccloud


def exponential_backoff(fun):
    for tries in range(5):
        try:
            fun()
            return
        except Exception as e:
            print(e)
            print(f'Retrying {tries}')
            time.sleep(2**tries)
    raise ValueError("Number of tries exceeded")

if __name__ == '__main__':
    print('Getting Baremetal Catalog')
    exponential_backoff(baremetal)
    print('Getting Private Cloud Catalog')
    exponential_backoff(privatecloud)
    print('Getting Public Cloud Catalog')
    exponential_backoff(publiccloud)