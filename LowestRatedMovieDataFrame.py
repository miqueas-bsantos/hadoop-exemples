from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql import functions
import logging
import boto3
from botocore.exceptions import ClientError
import os
from io import StringIO, BytesIO
import pandas as pd
import chardet

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.resource('s3')
    s3_client = s3_client.Bucket(name=bucket)
    try:
        response = s3_client.upload_fileobj(file_name, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def download_file(file_name, bucket):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    try:
        session = boto3.Session(profile_name='default')
        s3_client = session.resource('s3')
        obj = s3_client.Object(bucket, file_name)
        data = obj.get()["Body"].read()
        encoding = chardet.detect(data)
        return data.decode(encoding['encoding'])        
    except Exception as error:
        return str(error)

def loadMovieNames(file):
    movieNames = {}
    for line in file.split('\n'):
        # print(line, "*"*50)
        fields = line.split('|')
        try:
            movieNames[int(fields[0])] = fields[1]
        except Exception as error:
            print(error)
            print(line)
            print(fields)
    return movieNames

def parseInput(line):
    #print(line.split(), "#"*50)
    fields = line.split()
    return Row(movieID = int(fields[1]), rating = float(fields[2]))    

if __name__ == "__main__":
    # Create a SparkSession (the config bit is only for Windows!)
    spark = SparkSession.builder.appName("PopularMovies").getOrCreate()

    # Load up our movie ID -> name dictionary
    movieNames = loadMovieNames(download_file("dados/u.item", "senac-datalake-miqueas"))

    # Get the raw data
    lines = spark.sparkContext.textFile("hdfs:///user/maria_dev/ml-100k/u.data")
    # Convert it to a RDD of Row objects with (movieID, rating)
    movies = lines.map(parseInput)
    # Convert that to a DataFrame
    movieDataset = spark.createDataFrame(movies)
    # averageRatings = popularTotalsAndCount.mapValues(lambda totalAndCount : totalAndCount[0] / totalAndCount[1])

    # Sort b
    # Compute average rating for each movieID
    averageRatings = movieDataset.groupBy("movieID").avg("rating")

    # Compute count of ratings for each movieID
    counts = movieDataset.groupBy("movieID").count()
    print(counts.columns)

    # Join the two together (We now have movieID, avg(rating), and count columns)
    averagesAndCounts = counts.join(averageRatings, "movieID")

    # Pull the top 10 results
    topTen = averagesAndCounts.orderBy("avg(rating)").take(10)
    topMostRatingTen = averagesAndCounts.orderBy("avg(rating)", ascending=False).take(10)

    # Print them out, converting movie ID's to names as we go.
    final_df = []

    for movie in topTen:
        final_df.append((movieNames[movie[0]], movie[1], movie[2]))
        print (movieNames[movie[0]], movie[1], movie[2])    
    #final_df = spark.createDataFrame(final_df, ['name', 'quantity review', 'rating'])
    buffer = BytesIO()
    pd.DataFrame(final_df, columns=['movie_name', 'quantity_review', 'rating']).to_csv(path_or_buf=buffer, header=True, index=False)
    # Stop the session    
    response = upload_file(buffer.getvalue(), "senac-datalake-miqueas", "script/lowest_movie_rated.csv")
    if response: print("Success full upload **********************************************************************")
    print(averagesAndCounts.columns, "#"*50)
    final_df = []
    for movie in topMostRatingTen:
        final_df.append((movieNames[movie[0]], movie[1], movie[2]))
        print(movieNames[movie[0]], movie[1], movie[2])    
    buffer = BytesIO()
    pd.DataFrame(final_df, columns=['movie_name', 'quantity_review', 'rating']).to_csv(path_or_buf=buffer, header=True, index=False)
    response = upload_file(buffer.getvalue(), "senac-datalake-miqueas", "script/highest_movie_rated.csv")
    if response: print("Success full upload **********************************************************************")
    spark.stop()    