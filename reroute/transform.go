package main

import (
	"encoding/json"
	"errors"
	"log"
	"github.com/redpanda-data/redpanda/src/transform-sdk/go/transform"
)

func main() {
    transform.OnRecordWritten(delegateNPC)
}

type NPCMessage struct {
	Who string `json:"who"`
	Msg string `json:"msg"`
}

// doTransform is where you read the record that was written, and then you can
// output new records that will be written to the destination topic
func delegateNPC(e transform.WriteEvent, w transform.RecordWriter) error {
	// Assuming e.Record() returns []byte, if not you might need to adjust this line
	var npcMsg NPCMessage

	if err := json.Unmarshal(e.Record().Value, &npcMsg); err != nil {
		log.Println("Error parsing JSON:", err)
		return err
	}

	record := transform.Record{
		Key:   e.Record().Key,      // Presuming e.Record().Key is already of a type []byte
		Value: []byte(npcMsg.Msg),  // Convert string to []byte
	}
	log.Printf(" 'who': %s", npcMsg.Who)
	// Use a switch statement to handle different 'who' cases
	switch npcMsg.Who {
		case "npc1":
			// Logic for npc1
			return w.Write(record, transform.ToTopic("npc1-request"))
		case "npc2":
			// Logic for npc2
			return w.Write(record, transform.ToTopic("npc2-request"))
		case "npc3":
			// Logic for npc2
			return w.Write(record, transform.ToTopic("npc3-request"))
		default:
			// Handle unknown or unspecified 'who'
			log.Printf("Unknown 'who': %s", npcMsg.Who)
			return errors.New("unknown handler for 'who'")
		//	return w.Write(e.Record(),transform.toTopic("npc3-request"))
	}

	// If no errors, write the record as normal
	//return w.Write(e.Record())
}
