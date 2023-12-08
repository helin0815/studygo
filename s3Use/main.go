package main

import (
	"encoding/json"
	"fmt"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
)

type Config struct {
	Address string `json:"address"`
}

type Sample struct {
	Name     string `json:"name"`
	Intro    string `json:"intro"`
	Language string `json:"language"`
	ZipUrl   string `json:"zipUrl"`
}

type Client struct {
	cfg *Config
}

func NewClient(cfg *Config) *Client {
	return &Client{cfg: cfg}
}

func main() {
	getTemplates()
}

var (
	accessKey = "---" //""
	secretKey = "---" //""
	region    = "---"
	endpoint  = "s3.----.com"
)

func createS3Client() (*s3.S3, error) {
	sess, err := session.NewSession(&aws.Config{
		Credentials: credentials.NewStaticCredentials(accessKey, secretKey, ""),
		Endpoint:    aws.String(endpoint),
		Region:      aws.String(region),
		//minio:true,oss:false
		S3ForcePathStyle: aws.Bool(false),
	})
	if err != nil {
		return nil, err
	}
	s3Svc := s3.New(sess)
	return s3Svc, nil
}

func getTemplates() {
	s3Client, err := createS3Client()
	if err != nil {
		return
	}
	downloader := s3manager.NewDownloaderWithClient(s3Client, func(downloader *s3manager.Downloader) {
		downloader.PartSize = 4 * 1024 * 1024 // samples.json最大4MB
	})
	buf := aws.NewWriteAtBuffer([]byte{})
	_, err = downloader.Download(buf, &s3.GetObjectInput{
		Bucket: aws.String("---"),
		Key:    aws.String("---"),
	})
	if err != nil {
		panic(err)
	}
	results := make([]Sample, 0)
	if err := json.Unmarshal(buf.Bytes(), &results); err != nil {
		return
	}
	fmt.Println(results)
}
