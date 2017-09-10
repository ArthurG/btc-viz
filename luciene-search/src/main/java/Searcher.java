import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.StringField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexableField;
import org.apache.lucene.index.Term;
import org.apache.lucene.search.BooleanClause;
import org.apache.lucene.search.BooleanQuery;
import org.apache.lucene.search.BooleanQuery.Builder;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TermQuery;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.QueryBuilder;

public class Searcher {
	public static void main(String[] args) throws IOException {
		Path path = Paths.get("/mnt/3TB/LucieneIdx");
		Directory indexDirectory = FSDirectory.open(path);
		IndexReader reader = DirectoryReader.open(indexDirectory);
		IndexSearcher search = new IndexSearcher(reader);
		Query q = new TermQuery(new Term(LuceneConstants.WalletId, "1Gb94zFdMABFHifpXcj6p3efzqgNAXA48M"));
		TopDocs docs = search.search(q, 100);
		ScoreDoc[] scoreDocs = docs.scoreDocs;
		// Get the transaction that wallet is involved in
		Builder neighbouringWallets = new BooleanQuery.Builder();
		for (ScoreDoc scoreDoc : scoreDocs) {
			Document doc = reader.document(scoreDoc.doc);
			neighbouringWallets.add(
					new TermQuery(new Term(LuceneConstants.TransactionHash, doc.get(LuceneConstants.TransactionHash))),
					BooleanClause.Occur.SHOULD);

			/*
			 * System.out.println(doc.get(LuceneConstants.TransactionHash));
			 * System.out.println(doc.getField(LuceneConstants.TxAmount).
			 * numericValue());
			 * System.out.println(doc.get(LuceneConstants.TxType));
			 * System.out.println(doc.get(LuceneConstants.WalletId));
			 */
		}
		// Get Wallets that are 1 step from the transaction
		TopDocs walletsStep2 = search.search(neighbouringWallets.build(), BooleanQuery.getMaxClauseCount());
		for (ScoreDoc scoreDoc : walletsStep2.scoreDocs) {
			Document doc = reader.document(scoreDoc.doc);

			IndexableField txField = doc.getField(LuceneConstants.TransactionHash);
			IndexableField f = doc.getField(LuceneConstants.TxAmount);
			IndexableField g = doc.getField(LuceneConstants.TxType);
			IndexableField h = doc.getField(LuceneConstants.WalletId);
			/*
			 * System.out.println(txField.stringValue());
			 * System.out.println(f.stringValue());
			 * System.out.println(g.stringValue());
			 * System.out.println(h.stringValue());
			 */
		}

	}
}
