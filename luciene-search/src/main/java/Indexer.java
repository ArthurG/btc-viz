import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StoredField;
import org.apache.lucene.document.StringField;
import org.apache.lucene.index.CorruptIndexException;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

public class Indexer {

	private IndexWriter writer;
	Directory indexDirectory;

	public Indexer(String indexDirectoryPath) throws IOException {
		// this directory will contain the indexes
		Path path = Paths.get(indexDirectoryPath);
		indexDirectory = FSDirectory.open(path);

		// create the indexer
		IndexWriterConfig config = new IndexWriterConfig(new StandardAnalyzer());
		config.setOpenMode(IndexWriterConfig.OpenMode.CREATE);
		writer = new IndexWriter(indexDirectory, config);
	}

	public void close() throws CorruptIndexException, IOException {
		writer.close();
		indexDirectory.close();
	}

	public static Document makeTx(String txHash, String walletId, long txAmount, String txType) throws IOException {
		Document document = new Document();

		// index transaction hash
		Field transactionId = new StringField(LuceneConstants.TransactionHash, txHash, Field.Store.YES);

		// index wallet id
		Field walletField = new StringField(LuceneConstants.WalletId, walletId, Field.Store.YES);

		// index transaction amount
		Field txAmountField = new StoredField(LuceneConstants.TxAmount, txAmount);

		Field txTypeField = new StoredField(LuceneConstants.TxType, txType);

		document.add(transactionId);
		document.add(walletField);
		document.add(txAmountField);
		document.add(txTypeField);

		return document;
	}

	public void createIndex(String dataDirPath, String txType) throws IOException {
		// get all files in the data directory
		try {
			String inLoc = "/mnt/3TB/in.csv";
			BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream(inLoc), "UTF-8"));

			String line;
			boolean first = true;
			while ((line = br.readLine()) != null) {
				String[] items = line.split(",");
				if (items.length > 3) {
					continue;
				}
				Document doc = makeTx(items[0], items[1], Long.parseLong(items[2]), txType);
				writer.addDocument(doc);
			}
			br.close();

		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	public static void main(String[] args) throws IOException {
		System.out.println("Spot 1");
		String inLoc = "/mnt/3TB/btc_transaction_in.csv";
		String outLoc = "/mnt/3TB/btc_transaction_out.csv";
		Indexer idxr = new Indexer("/mnt/3TB/LucieneIdx");
		System.out.println("Spot 2");
		idxr.createIndex(inLoc, "RECEIEVED");
		idxr.createIndex(outLoc, "SENT");
		System.out.println("Spot 3");
		idxr.close();
	}
}