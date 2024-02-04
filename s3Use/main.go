package main

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/samber/lo"
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
	*s3.S3
}

func NewClient(cfg *Config) *Client {
	return &Client{cfg: cfg}
}

func main() {
	clientS3 := NewClient(nil)
	clientS3.getTemplates()
}

var (
	accessKey = "fb483d4a4912494c8ef4e4c7d422e1c4" //""
	secretKey = "8312e297a7644bf486e293cebb4ddb1b" //""
	region    = "bj"
	endpoint  = "s3.bj.bcebos.com"
)

func (s *Client) createS3Client() (*s3.S3, error) {
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

func (s *Client) getTemplates() {
	s3Client, err := s.createS3Client()
	if err != nil {
		return
	}
	downloader := s3manager.NewDownloaderWithClient(s3Client, func(downloader *s3manager.Downloader) {
		downloader.PartSize = 4 * 1024 * 1024 // samples.json最大4MB
	})
	buf := aws.NewWriteAtBuffer([]byte{})
	_, err = downloader.Download(buf, &s3.GetObjectInput{
		Bucket: aws.String("faas-function"),
		Key:    aws.String("lifaas-samples" + "/samples.json"),
	})
	if err != nil {
		panic(err)
	}
	results := make([]Sample, 0)
	if err := json.Unmarshal(buf.Bytes(), &results); err != nil {
		return
	}
	results = lo.Map(results, func(item Sample, index int) Sample {
		item.ZipUrl = "https://s3.bj.bcebos.com" + "/faas-function/lifaas-samples" + item.ZipUrl
		fmt.Println("原来的", item.ZipUrl)
		singedUrl, _ := s.GetPreSignURL("lifaas-samples")
		item.ZipUrl = singedUrl
		fmt.Println("现在的", item.ZipUrl)
		return item
	})

	fmt.Println("results")
}

func (s *Client) GetPreSignURL(key string) (string, error) {
	input := &s3.GetObjectInput{
		Bucket: aws.String("faas-function"),
		Key:    aws.String(key + "/samples.json"),
	}

	req, _ := s.GetObjectRequest(input)
	return req.Presign(time.Hour)
}
