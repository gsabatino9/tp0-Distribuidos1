package common

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	log "github.com/sirupsen/logrus"
)

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
	sigChan chan os.Signal
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
		sigChan: make(chan os.Signal, 1),
	}

	// Register signal handler for SIGTERM
	signal.Notify(client.sigChan, syscall.SIGTERM)
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Fatalf(
	        "action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	// autoincremental msgID to identify every message sent
	msgID := 1

loop:
	// Send messages if the loopLapse threshold has not been surpassed
	for timeout := time.After(c.config.LoopLapse); ; {
		select {
		case <-timeout:
	        log.Infof("action: timeout_detected | result: success | client_id: %v",
                c.config.ID,
            )
			break loop
		case <-c.sigChan:
			log.Infof("action: signal_received | result: success | client_id: %v", c.config.ID)
			log.Debugf("action: close_resource | result: in_progress | resource: socket | client_id: %v", c.config.ID)
			c.conn.Close()
			log.Infof("action: close_resource | result: success | resource: socket | client_id: %v", c.config.ID)
			break loop
		default:
		}

		// Create the connection the server in every loop iteration. Send an
		c.createClientSocket()

		// TODO: Modify the send to avoid short-write
		fmt.Fprintf(
			c.conn,
			"[CLIENT %v] Message N°%v\n",
			c.config.ID,
			msgID,
		)
		msg, err := bufio.NewReader(c.conn).ReadString('\n')
		msgID++
		c.conn.Close()

		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
                c.config.ID,
				err,
			)
			return
		}
		log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
            c.config.ID,
            msg,
        )

		// Wait a time between sending one message and the next one
		timeout := time.After(c.config.LoopPeriod)
		select {
		case <-timeout:
		case <-c.sigChan:
			log.Infof("action: signal_received | result: success | client_id: %v", c.config.ID)
			log.Infof("action: close_resource | result: success | resource: socket | client_id: %v | msg: socket already closed", c.config.ID)
			return
		}
		
	}

	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
