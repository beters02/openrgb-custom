package printutil

import (
	"fmt"
	"os"
	"strconv"
)

type StdType string

type Printable interface {
	~string | ~float64 | ~bool | ~int64 | ~uint64
}

const (
	StdOut StdType = "out"
	StdErr StdType = "err"
)

func stdType2File(stdType StdType) *os.File {
	if stdType == StdOut {
		return os.Stdout
	} else if stdType == StdErr {
		return os.Stderr
	}
	return nil
}

func fstd_main[T Printable](stdType StdType, msg T) {
	nmsg := ""
	switch x := any(msg).(type) {
	case string:
		nmsg = x
	case float64:
		nmsg = strconv.FormatFloat(x, 'f', 2, 64)
	case bool:
		nmsg = strconv.FormatBool(x)
	case int64:
		nmsg = strconv.FormatInt(x, 10)
	case uint64:
		nmsg = strconv.FormatUint(x, 10)
	default:
		panic("unhandled print type")
	}

	fmt.Fprintln(stdType2File(stdType), nmsg)
}

func Stdout[T Printable](msg T) {
	fstd_main(StdOut, msg)
}

func Stderr[T Printable](msg T) {
	fstd_main(StdErr, msg)
}
