import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Path;
import java.util.ArrayList;

import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexableField;
import org.apache.lucene.index.Term;
import org.apache.lucene.search.BooleanClause;
import org.apache.lucene.search.BooleanQuery;
import org.apache.lucene.search.BooleanQuery.Builder;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TermQuery;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

public class Searcher {
	public static void main(String[] args) throws IOException {
		Path path = FileSystems.getDefault().getPath("/mnt/3TB/", "LucieneIdx.luc");
		Directory indexDirectory = FSDirectory.open(path);
		IndexReader reader = DirectoryReader.open(indexDirectory);
		IndexSearcher search = new IndexSearcher(reader);
		TopDocs d = search.search(new TermQuery(new Term("1Q2TWHE3GMdB6BZKafqwxXtWAWgFt5Jvm3")), BooleanQuery.getMaxClauseCount());
		ScoreDoc[] s = d.scoreDocs;
		//Get the transaction that wallet is involved in
		Builder neighbouringWallets = new BooleanQuery.Builder();
		for (ScoreDoc scoreDoc : s) {
			Document doc = reader.document(scoreDoc.doc);
			IndexableField txField = doc.getField(LuceneConstants.TransactionHash);
			neighbouringWallets.add(new TermQuery(new Term(txField.stringValue())), BooleanClause.Occur.SHOULD);
			IndexableField f = doc.getField(LuceneConstants.TxAmount);
			f.stringValue();
			IndexableField g = doc.getField(LuceneConstants.TxType);
			g.stringValue();
			IndexableField h = doc.getField(LuceneConstants.WalletId);
			h.stringValue();
		}
		//Get Wallets that are 1 step from the transaction
		TopDocs walletsStep2 = search.search(neighbouringWallets.build(), BooleanQuery.getMaxClauseCount());
		for (ScoreDoc scoreDoc : s) {
			Document doc = reader.document(scoreDoc.doc);

			IndexableField txField = doc.getField(LuceneConstants.TransactionHash);
			System.out.println(txField.stringValue());
			IndexableField f = doc.getField(LuceneConstants.TxAmount);
			System.out.println(f.stringValue());
			IndexableField g = doc.getField(LuceneConstants.TxType);
			System.out.println(g.stringValue());
			IndexableField h = doc.getField(LuceneConstants.WalletId);
			System.out.println(h.stringValue());
		}
		

	}
}
