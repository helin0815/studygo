package main

import (
	"fmt"
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

func scheduledNotifacation(t time.Duration) <-chan struct{} {
	ch := make(chan struct{}, 1)
	go func() {
		time.Sleep(t)
		ch <- struct{}{}
	}()
	return ch
}
func main() {

	fmt.Println("first send")
	//<-ch 是从通道读取操作，它是一个阻塞操作。如果通道 ch 中没有数据，那么主函数就会在这里阻塞，直到 ch 中有数据可读。
	<-scheduledNotifacation(time.Second * 1) // 这里加了<- 就变成了阻塞的，如果没有<- 就变成了非阻塞的
	fmt.Println("second send")
	<-scheduledNotifacation(time.Second * 2)
	fmt.Println("third send")
}
