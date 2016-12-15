from jobqueue import JobQueue, Job


def job_callback(job):
    print(repr(job))
    print('Test message')


def main():
    job = Job(interval=10, task=job_callback)
    job2 = Job(interval=4, task=job_callback)

    jobqueue = JobQueue()
    jobqueue.put(job)
    jobqueue.start()
    jobqueue.put(job2)

    print('Non blocking')


if __name__ == "__main__":
    main()
