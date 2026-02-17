"""
Knowledge graph construction and management for ResilienceAI.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re

from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


@dataclass
class Concept:
    """Knowledge graph concept."""
    concept_id: str
    name: str
    description: str
    concept_type: str
    category: str
    synonyms: List[str] = None
    source: str = ""
    confidence: float = 1.0


@dataclass
class Document:
    """Knowledge source document."""
    document_id: str
    title: str
    document_type: str
    source_url: str = ""
    publication_date: str = ""
    author: str = ""
    organization: str = ""
    jurisdiction: str = ""
    keywords: List[str] = None
    summary: str = ""


class KnowledgeGraphBuilder:
    """Builds and manages the ResilienceAI knowledge graph."""
    
    # Hazard-related concepts
    HAZARD_CONCEPTS = {
        "flood": {
            "synonyms": ["flooding", "inundation", "deluge"],
            "related": ["storm_surge", "flash_flood", "riverine_flood"],
            "category": "natural_hazard"
        },
        "earthquake": {
            "synonyms": ["seismic_event", "tremor", "quake"],
            "related": ["ground_shaking", "liquefaction", "tsunami"],
            "category": "natural_hazard"
        },
        "hurricane": {
            "synonyms": ["typhoon", "cyclone", "tropical_storm"],
            "related": ["storm_surge", "high_winds", "heavy_rainfall"],
            "category": "natural_hazard"
        },
        "wildfire": {
            "synonyms": ["brush_fire", "forest_fire", "grass_fire"],
            "related": ["smoke", "evacuation", "air_quality"],
            "category": "natural_hazard"
        },
        "drought": {
            "synonyms": ["water_shortage", "dry_spell"],
            "related": ["water_restriction", "crop_loss", "wildfire_risk"],
            "category": "natural_hazard"
        }
    }
    
    # Mitigation concepts
    MITIGATION_CONCEPTS = {
        "elevation": {
            "synonyms": ["raise", "lift", "heighten"],
            "related": ["flood_proofing", "building_modification"],
            "category": "mitigation_strategy"
        },
        "retrofit": {
            "synonyms": ["strengthen", "reinforce", "upgrade"],
            "related": ["seismic_retrofit", "wind_retrofit"],
            "category": "mitigation_strategy"
        },
        "evacuation": {
            "synonyms": ["relocate", "withdraw", "move_out"],
            "related": ["emergency_management", "public_safety"],
            "category": "response_strategy"
        },
        "early_warning": {
            "synonyms": ["alert", "notification", "forecast"],
            "related": ["monitoring", "prediction", "communication"],
            "category": "preparedness_strategy"
        }
    }
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def initialize_knowledge_base(self) -> Dict[str, int]:
        """
        Initialize the knowledge graph with core concepts.
        
        Returns:
            Statistics about created entities
        """
        stats = {"concepts": 0, "relationships": 0}
        
        # Create hazard concepts
        for concept_name, concept_data in self.HAZARD_CONCEPTS.items():
            self._create_concept(
                concept_id=f"hazard_{concept_name}",
                name=concept_name.replace("_", " ").title(),
                description=f"Natural hazard: {concept_name}",
                concept_type="hazard",
                category=concept_data["category"],
                synonyms=concept_data["synonyms"]
            )
            stats["concepts"] += 1
            
            # Create related concepts
            for related in concept_data["related"]:
                self._create_concept(
                    concept_id=f"hazard_{related}",
                    name=related.replace("_", " ").title(),
                    description=f"Related to {concept_name}",
                    concept_type="hazard_aspect",
                    category="hazard_component",
                    synonyms=[]
                )
                stats["concepts"] += 1
                
                # Create relationship
                self._create_concept_relationship(
                    f"hazard_{concept_name}",
                    f"hazard_{related}",
                    "HAS_ASPECT"
                )
                stats["relationships"] += 1
        
        # Create mitigation concepts
        for concept_name, concept_data in self.MITIGATION_CONCEPTS.items():
            self._create_concept(
                concept_id=f"mitigation_{concept_name}",
                name=concept_name.replace("_", " ").title(),
                description=f"Mitigation strategy: {concept_name}",
                concept_type="mitigation",
                category=concept_data["category"],
                synonyms=concept_data["synonyms"]
            )
            stats["concepts"] += 1
        
        # Create hazard-mitigation relationships
        hazard_mitigation_pairs = [
            ("hazard_flood", "mitigation_elevation"),
            ("hazard_earthquake", "mitigation_retrofit"),
            ("hazard_hurricane", "mitigation_evacuation"),
            ("hazard_wildfire", "mitigation_evacuation"),
        ]
        
        for hazard, mitigation in hazard_mitigation_pairs:
            self._create_concept_relationship(hazard, mitigation, "ADDRESSED_BY")
            stats["relationships"] += 1
        
        return stats
    
    def _create_concept(self, **kwargs) -> None:
        """Create a concept node."""
        query = """
        MERGE (c:Concept {concept_id: $concept_id})
        SET c.name = $name,
            c.description = $description,
            c.concept_type = $concept_type,
            c.category = $category,
            c.synonyms = $synonyms,
            c.source = $source,
            c.confidence = $confidence,
            c.created_at = datetime()
        """
        self.manager.execute_write(query, {
            **kwargs,
            "source": kwargs.get("source", "system"),
            "confidence": kwargs.get("confidence", 1.0),
            "synonyms": kwargs.get("synonyms", [])
        })
    
    def _create_concept_relationship(
        self,
        from_id: str,
        to_id: str,
        rel_type: str,
        properties: Dict[str, Any] = None
    ) -> None:
        """Create relationship between concepts."""
        props_str = ""
        if properties:
            props_str = ", " + ", ".join(f"r.{k} = ${k}" for k in properties.keys())
        
        query = f"""
        MATCH (c1:Concept {{concept_id: $from_id}})
        MATCH (c2:Concept {{concept_id: $to_id}})
        MERGE (c1)-[r:{rel_type}]->(c2)
        {props_str}
        """
        
        params = {"from_id": from_id, "to_id": to_id, **(properties or {})}
        self.manager.execute_write(query, params)
    
    def ingest_document(self, document: Document, extract_concepts: bool = True) -> Dict[str, Any]:
        """
        Ingest a document into the knowledge graph.
        
        Args:
            document: Document to ingest
            extract_concepts: Whether to extract concepts from document
            
        Returns:
            Ingestion results
        """
        # Create document node
        query = """
        MERGE (d:Document {document_id: $doc_id})
        SET d.title = $title,
            d.document_type = $doc_type,
            d.source_url = $url,
            d.publication_date = date($pub_date),
            d.author = $author,
            d.organization = $org,
            d.jurisdiction = $jurisdiction,
            d.keywords = $keywords,
            d.summary = $summary,
            d.ingested_at = datetime()
        RETURN d
        """
        
        self.manager.execute_write(query, {
            "doc_id": document.document_id,
            "title": document.title,
            "doc_type": document.document_type,
            "url": document.source_url,
            "pub_date": document.publication_date,
            "author": document.author,
            "org": document.organization,
            "jurisdiction": document.jurisdiction,
            "keywords": document.keywords or [],
            "summary": document.summary
        })
        
        results = {"document_id": document.document_id, "concepts_extracted": 0}
        
        # Extract and link concepts
        if extract_concepts and document.summary:
            concepts = self._extract_concepts_from_text(document.summary)
            for concept in concepts:
                self._link_document_to_concept(document.document_id, concept)
                results["concepts_extracted"] += 1
        
        return results
    
    def _extract_concepts_from_text(self, text: str) -> List[str]:
        """Extract concepts from text using keyword matching."""
        text_lower = text.lower()
        found_concepts = []
        
        all_concepts = {**self.HAZARD_CONCEPTS, **self.MITIGATION_CONCEPTS}
        
        for concept_name, concept_data in all_concepts.items():
            # Check main name
            if concept_name.replace("_", " ") in text_lower:
                found_concepts.append(
                    f"hazard_{concept_name}" if concept_name in self.HAZARD_CONCEPTS 
                    else f"mitigation_{concept_name}"
                )
                continue
            
            # Check synonyms
            for synonym in concept_data.get("synonyms", []):
                if synonym.lower() in text_lower:
                    found_concepts.append(
                        f"hazard_{concept_name}" if concept_name in self.HAZARD_CONCEPTS 
                        else f"mitigation_{concept_name}"
                    )
                    break
        
        return list(set(found_concepts))
    
    def _link_document_to_concept(self, document_id: str, concept_id: str) -> None:
        """Link a document to a concept."""
        query = """
        MATCH (d:Document {document_id: $doc_id})
        MATCH (c:Concept {concept_id: $concept_id})
        MERGE (d)-[:MENTIONS]->(c)
        """
        self.manager.execute_write(query, {
            "doc_id": document_id,
            "concept_id": concept_id
        })
    
    def query_knowledge(
        self,
        query_text: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Query the knowledge graph for relevant information.
        
        Args:
            query_text: Query text
            max_results: Maximum results to return
            
        Returns:
            Relevant knowledge items
        """
        # Extract concepts from query
        query_concepts = self._extract_concepts_from_text(query_text)
        
        # Search for relevant documents and concepts
        search_query = """
        // Match query concepts
        UNWIND $query_concepts AS concept_id
        MATCH (qc:Concept {concept_id: concept_id})
        
        // Find related concepts
        OPTIONAL MATCH (qc)-[:RELATED_TO|HAS_ASPECT*1..2]-(related:Concept)
        
        // Find documents mentioning these concepts
        WITH collect(DISTINCT qc) + collect(DISTINCT related) AS all_concepts
        UNWIND all_concepts AS concept
        
        OPTIONAL MATCH (d:Document)-[:MENTIONS]->(concept)
        OPTIONAL MATCH (d)-[:DESCRIBES]->(bp:BestPractice)
        OPTIONAL MATCH (d)-[:IMPLEMENTS]->(r:Regulation)
        
        RETURN DISTINCT
            d.document_id AS doc_id,
            d.title AS title,
            d.document_type AS doc_type,
            d.jurisdiction AS jurisdiction,
            collect(DISTINCT concept.name) AS matched_concepts,
            collect(DISTINCT bp.name) AS best_practices,
            collect(DISTINCT r.title) AS regulations,
            count(DISTINCT concept) AS concept_matches
        ORDER BY concept_matches DESC
        LIMIT $max_results
        """
        
        return self.manager.execute_read(
            search_query,
            {"query_concepts": query_concepts, "max_results": max_results}
        )
    
    def get_concept_hierarchy(self, root_concept_id: str) -> Dict[str, Any]:
        """
        Get hierarchical structure of a concept.
        
        Args:
            root_concept_id: Root concept ID
            
        Returns:
            Concept hierarchy
        """
        query = """
        MATCH (root:Concept {concept_id: $root_id})
        CALL apoc.path.subgraphAll(root, {
            relationshipFilter: 'HAS_ASPECT|PART_OF|RELATED_TO>',
            minLevel: 0,
            maxLevel: 3
        }) YIELD nodes, relationships
        
        RETURN {
            root: root {.*},
            nodes: [n IN nodes | n {.*}],
            relationships: [r IN relationships | {
                from: startNode(r).concept_id,
                to: endNode(r).concept_id,
                type: type(r)
            }]
        } AS hierarchy
        """
        
        result = self.manager.execute_read(query, {"root_id": root_concept_id})
        return result[0]['hierarchy'] if result else {}


class KnowledgeGraphQuery:
    """Query interface for the knowledge graph."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def find_related_hazards(self, concept_name: str) -> List[Dict[str, Any]]:
        """Find hazards related to a concept."""
        query = """
        MATCH (c:Concept)
        WHERE c.name CONTAINS $name OR $name IN c.synonyms
        MATCH (c)-[:RELATED_TO|ADDRESSED_BY*1..3]-(h:Concept)
        WHERE h.concept_type = 'hazard'
        RETURN DISTINCT h.name AS hazard_name,
               h.concept_id AS hazard_id,
               h.description AS description
        """
        
        return self.manager.execute_read(query, {"name": concept_name})
    
    def find_mitigation_strategies(
        self,
        hazard_name: str,
        facility_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find mitigation strategies for a hazard."""
        query = """
        MATCH (h:Concept)
        WHERE h.name CONTAINS $hazard_name OR $hazard_name IN h.synonyms
        MATCH (h)-[:ADDRESSED_BY]-(m:Concept)
        WHERE m.concept_type = 'mitigation'
        
        OPTIONAL MATCH (m)-[:REQUIRES]->(r:Resource)
        OPTIONAL MATCH (bp:BestPractice)-[:ADDRESSES]->(m)
        
        RETURN m.name AS strategy_name,
               m.description AS description,
               m.category AS strategy_type,
               collect(DISTINCT r.name) AS required_resources,
               collect(DISTINCT bp.name) AS best_practices
        ORDER BY m.confidence DESC
        """
        
        return self.manager.execute_read(query, {"hazard_name": hazard_name})
    
    def get_regulatory_requirements(
        self,
        county_fips: str,
        facility_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get regulatory requirements for a county."""
        query = """
        MATCH (c:County {fips_code: $fips_code})
        MATCH (r:Regulation)-[:APPLIES_TO]->(c)
        
        OPTIONAL MATCH (r)-[:REQUIRES]->(req:Concept)
        OPTIONAL MATCH (d:Document)-[:IMPLEMENTS]->(r)
        
        RETURN r.regulation_id AS regulation_id,
               r.title AS title,
               r.regulation_type AS level,
               r.issuing_authority AS authority,
               r.effective_date AS effective_date,
               collect(DISTINCT req.name) AS requirements,
               collect(DISTINCT d.title) AS reference_documents
        ORDER BY r.effective_date DESC
        """
        
        return self.manager.execute_read(query, {"fips_code": county_fips})
