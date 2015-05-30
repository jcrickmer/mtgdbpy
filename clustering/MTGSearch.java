/*package org.apache.lucene.demo;*/

/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Date;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.queryparser.classic.MultiFieldQueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;

/** Simple command-line based search demo. */
public class MTGSearch {

	private MTGSearch() {}

	/** Simple command-line based search demo. */
	public static void main(String[] args) throws Exception {
		String usage =
			"Usage:\tjava org.apache.lucene.demo.SearchFiles [-index dir] [-field f] [-queries file] [-query string] [-raw] [-paging hitsPerPage]\n\nSee http://lucene.apache.org/core/4_1_0/demo/ for details.";
		if (args.length > 0 && ("-h".equals(args[0]) || "-help".equals(args[0]))) {
			System.out.println(usage);
			System.exit(0);
		}

		String index = "index";
		String field = "contents";
		String queries = null;
		boolean raw = false;
		String queryString = null;
		int hitsPerPage = 19;
		File qFile = null;
		for(int i = 0;i < args.length;i++) {
			if ("-index".equals(args[i])) {
				index = args[i+1];
				i++;
			} else if ("-field".equals(args[i])) {
				field = args[i+1];
				i++;
			} else if ("-queries".equals(args[i])) {
				queries = args[i+1];
				i++;
				qFile = new File(queries);
			} else if ("-query".equals(args[i])) {
				queryString = args[i+1];
				i++;
			} else if ("-raw".equals(args[i])) {
				raw = true;
			} else if ("-paging".equals(args[i])) {
				hitsPerPage = Integer.parseInt(args[i+1]);
				if (hitsPerPage <= 0) {
					System.err.println("There must be at least 1 hit per page.");
					System.exit(1);
				}
				i++;
			}
		}
    
		IndexReader reader = DirectoryReader.open(FSDirectory.open(new File(index)));
		IndexSearcher searcher = new IndexSearcher(reader);
		Analyzer analyzer = new StandardAnalyzer(Version.LUCENE_40);

		QueryParser parser = new QueryParser(Version.LUCENE_40, field, analyzer);
		//MultiFieldQueryParser parser = new MultiFieldQueryParser(Version.LUCENE_40,
		//														 new String[] {"contents", "cmc"},
		//														 analyzer);
		for (int pc_id = 0; pc_id < 50000; pc_id++) {
			File cardDoc = new File("/tmp/cards_for_lucene/physicalcard_" + pc_id);
			if (! cardDoc.exists()) {
				continue;
			}
			BufferedReader in = new BufferedReader(new InputStreamReader(new FileInputStream(cardDoc), "UTF-8"));

			StringBuffer alldoc = new StringBuffer();
			String iline;
			while ((iline = in.readLine()) != null) {
				iline = iline.trim();
				alldoc.append(iline);
				alldoc.append(" ");
			}
			in.close();
			String line = alldoc.toString().toLowerCase();
			line = line.replace("/"," ");
			line = line.replace(","," ");
			line = line.replace("."," ");
			line = line.replace(":"," ");
			line = line.replace(";"," ");
			line = line.replace("{"," ");
			line = line.replace("}"," ");
			line = line.replace("?"," ");
			line = line.replace("~","\\~");
			line = line.replace("*","\\*");
			line = line.replace("-","\\-");
			line = line.replace("+","\\+");
			line = line.replace("|","\\|");
			line = line.replace("(","");
			line = line.replace(")","");
			line = line.replace("'","\\'");
			line = line.replace("\\","\\\\");

			//System.out.println("Searching for: " + line + "\n");
			Query query = parser.parse(line);
			//System.out.println("Searching for: " + query.toString());
            
			doPagingSearch(searcher, query, hitsPerPage, raw, queries == null && queryString == null, "" + pc_id);
		}
		reader.close();
	}
	
	/**
	 * This demonstrates a typical paging search scenario, where the search engine presents 
	 * pages of size n to the user. The user can then go to the next page if interested in
	 * the next hits.
	 * 
	 * When the query is executed for the first time, then only enough results are collected
	 * to fill 5 result pages. If the user wants to page beyond this limit, then the query
	 * is executed another time and all hits are collected.
	 * 
	 */
	public static void doPagingSearch(IndexSearcher searcher, Query query, 
									  int hitsPerPage, boolean raw, boolean interactive, String searchedId) throws IOException {
		// Collect enough docs to show 5 pages
		TopDocs results = searcher.search(query, 5 * hitsPerPage);
		ScoreDoc[] hits = results.scoreDocs;
    
		int numTotalHits = results.totalHits;
		//System.out.println(numTotalHits + " total matching documents");

		int start = 0;
		int end = Math.min(numTotalHits, hitsPerPage);
        
		for (int i = start; i < end; i++) {
			if (raw) {                              // output raw format
				System.out.println("doc="+hits[i].doc+" score="+hits[i].score);
				continue;
			}

			Document doc = searcher.doc(hits[i].doc);
			String path = doc.get("path");
			String physicalcardid = doc.get("physicalcardid");
			if (searchedId.equals(physicalcardid)) {
				continue;
			}
			System.out.print("INSERT INTO similarphysicalcard (physicalcard_id, sim_physicalcard_id, score) VALUES (");
			System.out.print(searchedId);
			System.out.print(",");
			System.out.print(physicalcardid);
			System.out.print(",");
			System.out.print(hits[i].score);
			System.out.print(");\n");
		}
			
	}
}
