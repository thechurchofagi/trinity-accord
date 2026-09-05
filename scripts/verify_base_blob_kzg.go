// Command verify-base-blob-kzg replays the trust-sensitive part of OP Stack
// batch fetching without any network access. Copy this file into a pinned
// optimism checkout and build it in that module.
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"reflect"
	"strings"

	"github.com/ethereum-optimism/optimism/op-node/cmd/batch_decoder/fetch"
	"github.com/ethereum-optimism/optimism/op-node/rollup/derive"
	"github.com/ethereum-optimism/optimism/op-service/eth"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
)

var (
	baseInbox   = common.HexToAddress("0xff00000000000000000000000000000000008453")
	baseBatcher = common.HexToAddress("0x5050f69a9786f081509234f1a7f4684b5e5b76c9")
)

func fail(format string, args ...any) {
	fmt.Fprintf(os.Stderr, "[BASE OFFLINE KZG FAIL] "+format+"\n", args...)
	os.Exit(1)
}

func main() {
	if len(os.Args) != 3 {
		fail("usage: verify-base-blob-kzg <decoder-transaction-dir> <blob-dir>")
	}
	txDir, blobDir := os.Args[1], os.Args[2]
	files, err := os.ReadDir(txDir)
	if err != nil {
		fail("read transactions: %v", err)
	}
	referenced := make(map[string]struct{})
	transactions, validTransactions, excludedTransactions, frames, blobs := 0, 0, 0, 0, 0
	for _, entry := range files {
		if entry.IsDir() || !strings.HasSuffix(entry.Name(), ".json") {
			continue
		}
		raw, err := os.ReadFile(filepath.Join(txDir, entry.Name()))
		if err != nil {
			fail("read %s: %v", entry.Name(), err)
		}
		var item fetch.TransactionWithMetadata
		if err := json.Unmarshal(raw, &item); err != nil {
			fail("decode %s: %v", entry.Name(), err)
		}
		if item.Tx == nil || item.Tx.Hash().Hex()+".json" != entry.Name() {
			fail("signed transaction/filename mismatch: %s", entry.Name())
		}
		if item.InboxAddr != baseInbox || item.ChainId != 8453 {
			fail("invalid Base transaction metadata: %s", item.Tx.Hash())
		}
		signer := types.LatestSignerForChainID(item.Tx.ChainId())
		recoveredSender, err := signer.Sender(item.Tx)
		if err != nil || recoveredSender != item.Sender {
			fail("signed sender recovery mismatch tx=%s sender=%s recovered=%s err=%v", item.Tx.Hash(), item.Sender, recoveredSender, err)
		}
		expectedValidSender := recoveredSender == baseBatcher
		if item.ValidSender != expectedValidSender {
			fail("cached sender validity mismatch tx=%s sender=%s", item.Tx.Hash(), recoveredSender)
		}
		var dataItems [][]byte
		if item.Tx.Type() == types.BlobTxType {
			for _, versionedHash := range item.Tx.BlobHashes() {
				name := strings.TrimPrefix(versionedHash.Hex(), "0x") + ".blob"
				blobRaw, err := os.ReadFile(filepath.Join(blobDir, name))
				if err != nil {
					fail("read blob %s: %v", versionedHash, err)
				}
				if len(blobRaw) != len(eth.Blob{}) {
					fail("blob size mismatch %s bytes=%d", versionedHash, len(blobRaw))
				}
				var blob eth.Blob
				copy(blob[:], blobRaw)
				commitment, err := blob.ComputeKZGCommitment()
				if err != nil {
					fail("compute KZG commitment %s: %v", versionedHash, err)
				}
				if actual := eth.KZGToVersionedHash(commitment); actual != versionedHash {
					fail("KZG versioned hash mismatch expected=%s actual=%s", versionedHash, actual)
				}
				data, err := blob.ToData()
				if err != nil {
					fail("decode blob field elements %s: %v", versionedHash, err)
				}
				dataItems = append(dataItems, data)
				referenced[name] = struct{}{}
				blobs++
			}
		} else {
			dataItems = append(dataItems, item.Tx.Data())
		}
		if len(item.ValidFrames) != len(dataItems) || len(item.FrameErrs) != len(dataItems) {
			fail("cached frame result population mismatch tx=%s", item.Tx.Hash())
		}
		var parsed []derive.Frame
		for i, data := range dataItems {
			value, err := derive.ParseFrames(data)
			if err != nil {
				if item.ValidFrames[i] || item.FrameErrs[i] != err.Error() {
					fail("cached frame error differs from replay tx=%s item=%d", item.Tx.Hash(), i)
				}
				if item.ValidSender {
					fail("canonical Base batcher submitted invalid frames tx=%s item=%d: %v", item.Tx.Hash(), i, err)
				}
				continue
			}
			if !item.ValidFrames[i] || item.FrameErrs[i] != "" {
				fail("cached valid frame differs from replay tx=%s item=%d", item.Tx.Hash(), i)
			}
			parsed = append(parsed, value...)
		}
		if !reflect.DeepEqual(parsed, item.Frames) {
			fail("archived frame cache differs from replay tx=%s", item.Tx.Hash())
		}
		transactions++
		if item.ValidSender {
			validTransactions++
		} else {
			excludedTransactions++
		}
		frames += len(parsed)
	}
	blobFiles, err := filepath.Glob(filepath.Join(blobDir, "*.blob"))
	if err != nil {
		fail("glob blobs: %v", err)
	}
	if len(blobFiles) != len(referenced) {
		fail("blob population mismatch files=%d referenced=%d", len(blobFiles), len(referenced))
	}
	for _, name := range blobFiles {
		if _, ok := referenced[filepath.Base(name)]; !ok {
			fail("unreferenced blob file %s", filepath.Base(name))
		}
	}
	if transactions == 0 || validTransactions == 0 || frames == 0 || blobs == 0 {
		fail("empty proof population txs=%d valid_txs=%d frames=%d blobs=%d", transactions, validTransactions, frames, blobs)
	}
	fmt.Printf("[BASE OFFLINE KZG PASS] transactions=%d canonical=%d excluded_senders=%d frames=%d blobs=%d unique_blobs=%d\n", transactions, validTransactions, excludedTransactions, frames, blobs, len(referenced))
}
