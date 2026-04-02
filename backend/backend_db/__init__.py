

#Based on db.py
    # our current method, for everyone using the repo, when the do docker compose up, so a new postgre/mongodb container would be established, which is not shared
    # a real remote server needs to be established which would be looking like "postgresql+asyncpg://preproai:StrongPassword123@db.mycompany.com:5432/preproai" in 17th line of db.py, similarly, the docker-compose
"""
    Lines 4–22: postgres service → remove, point POSTGRES_DSN to remote
    Lines 24–33: mongodb service → remove, point MONGO_DSN to remote
    Lines 38–45: redis service → remove, point REDIS_DSN to remote
    Lines 47–58: minio service → remove, point to remote S3/MinIO
    Lines 129–133: remove the corresponding volumes
"""
    # also provides the api for FastAPI with get_db_session() to get access to the database

#Based on MongoDB.py
    #similar to above, and also falls back to a local docker
    #mongo is a document database unlike Postgre which is a relational, so it can handle connections internally without the need of session from SQLAlchemy.
    # and the FastAPI dependency is the same, the api provided is get_mongo_database() to get access to the database


#db_models.py
    #this file declares the general structure of data to be stored in postgre format, starting from the Users side to tasks data and so on.
    #and for mongo, they are document based, so no strucutred definitions are required.

    #Updates:   
        #added relationships between tables, so you know which user did which task for example
        #modified User, TaskAssignment and QualityMetric tables to include the relationships, so that we can easily query related data across tables.

#db_interface.py
    #provides single access point to all database operations in the platform.
    #everyone who wants to write things into the database should use this interface

    #Updates:
        #AUTHORIZIATION
        #when the user login, from frontend, there is need to call get_user()
        #similarly at frontend register, there is need to call create_user()
        
        #Employer Part of creating tasks
        #creating and uploading contents exists
        # but viewing of created projects, get_project() needed
        # view all projects, list_projects()
        #similarly progress of the project is never updated, in order to track, needs update_project_progress()

        #Annotator Part of doing tasks
        #view task, claim tasks, submit tasks already exists as list_task_square(), claim_task() and submit_annotation()
        #But missing of get_task_with_content() which would be displaying teh content from mongodb in order for the annotator to annotate
        
        #Auditor Part of reviewing tasks
        #generally complete, mark_under_review() exists when task is submitted and waiting for reviewer to check
        #api for finalize_task() exists which flips the condtion from under review to finalized
        #record_quality_metric() for the feedback to be stored

        #Export flow
        #this part is missing entirely, which that the labeled data needs to be exported for the later RLHF or SFT
        #needs a export_finalized_tasks() which fetches the finalized takss and pulls the annotation results from mongo and exports them.


#overall in addition to the above, there is a general problem which exists for the method utcnow() which is deprecated after python 3.11