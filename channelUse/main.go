package main

import (
	"fmt"
	"math/rand"
	"time"
)

//1
//func longTimedOperation() <-chan int32 {
//	ch := make(chan int32)
//	go func() {
//		defer close(ch)
//		time.Sleep(time.Second * 3)
//		ch <- rand.Int31n(300)
//	}()
//	return ch
//}
//
//func main() {
//	ch := longTimedOperation()
//	fmt.Println(<-ch)
//
//}
// 2
//type T = struct {
//}
//
//func main() {
//	complted := make(chan T)
//	go func() {
//		fmt.Println("ping")
//		time.Sleep(time.Second * 2)
//		<-complted
//
//	}()
//	complted <- struct{}{}
//	fmt.Println("pong")
//}

// 3

// 20231201
//func scheduledNotifacation(t time.Duration) <-chan struct{} {
//	ch := make(chan struct{}, 1)
//	go func() {
//		time.Sleep(t)
//		ch <- struct{}{}
//	}()
//	return ch
//}
//func main() {
//
//	fmt.Println("first send")
//	//<-ch 是从通道读取操作，它是一个阻塞操作。如果通道 ch 中没有数据，那么主函数就会在这里阻塞，直到 ch 中有数据可读。
//	<-scheduledNotifacation(time.Second * 1) // 这里加了<- 就变成了阻塞的，如果没有<- 就变成了非阻塞的
//	fmt.Println("second send")
//	<-scheduledNotifacation(time.Second * 2)
//	fmt.Println("third send")
//}

// 20231204.1
//type dog struct {
//	Name  string
//	Color string
//}
//
//func main() {
//	allChan := make(chan interface{}, 10)
//	allChan <- dog{
//		Name:  "tom",
//		Color: "red",
//	}
//	allChan <- 1
//	allChan <- "nha"
//	//a := (<-allChan).(dog) // 如果这里取了，那么管道里就会少一个数据
//	//
//	//fmt.Println("aa:", a.Color)
//	close(allChan) // 管道关闭之后是不能再写入的

//for i := 0; i < len(allChan); i++ { // 这样子只能取两个指出来，但是本来有三个值。这样取值会不正确，因为取值之后len会变化
//	fmt.Println("allChan:", <-allChan)
//
//}

//for {
//	/*
//		val: {tom red}
//		val: 1
//		val: nha
//		管道里面已经没数据了
//	*/
//	val, ok := <-allChan
//	if !ok {
//		fmt.Println("管道里面已经没数据了")
//		break
//	}
//	fmt.Println("val:", val)
//}
//}

// 20231204.2 写一个同时往通道里写和读的代码
var intChan chan int

//
//func main() {
//	intChan = make(chan int, 50)
//	exitChan := make(chan bool)
//	go writeData(intChan)
//	go readData(intChan, exitChan)
//	time.Sleep(time.Second * 2)
//	fmt.Println("start")
//}

func writeData(intCh chan int) {
	rand.Seed(time.Now().UnixNano())
	for i := 1; i < 50; i++ {
		var tempInt int
		tempInt = rand.Intn(4) + 10
		intCh <- tempInt
		fmt.Println("writeData:", tempInt)
	}
	close(intChan)
}

func readData(intCh chan int, exitChan chan bool) {
	var count int
	for {
		val, ok := <-intCh
		count++
		if !ok {
			break
		}
		fmt.Println("读到谁，第几次:", val, count)
	}
	exitChan <- true
	close(intCh)
}

func isPrime(num int) {
	for i := 1; i <= num; i++ {
		var flag = true
		for j := 2; j < i; j++ {
			if i%j == 0 {
				flag = false
				continue
			}
		}
		if flag {
			fmt.Println("i是素数:", i)
		}
	}
}

func main() {
	isPrime(200)
}
