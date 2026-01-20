package com.travelassistant.attraction.repository;

import com.travelassistant.attraction.entity.Attraction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;

@Repository
public interface AttractionRepository extends JpaRepository<Attraction, java.util.UUID> {

  /**
   * 根据目的地查找景点
   */
  List<Attraction> findByDestination(String destination);

  /**
   * 根据类别查找景点
   */
  List<Attraction> findByCategory(String category);

  /**
   * 根据评分查找景点
   */
  @Query("SELECT a FROM Attraction a WHERE a.rating >= :minRating ORDER BY a.rating DESC")
  List<Attraction> findByMinRating(@Param("minRating") BigDecimal minRating);

  /**
   * 根据标签查找景点
   */
  @Query("SELECT a FROM Attraction a WHERE :tag = ANY(a.tags)")
  List<Attraction> findByTag(@Param("tag") String tag);

  /**
   * 根据目的地和类别查找景点
   */
  @Query("SELECT a FROM Attraction a WHERE a.destination = :destination AND a.category = :category")
  List<Attraction> findByDestinationAndCategory(
      @Param("destination") String destination,
      @Param("category") String category);

  /**
   * 根据目的地和标签查找景点
   */
  @Query("SELECT a FROM Attraction a WHERE a.destination = :destination AND :tag = ANY(a.tags)")
  List<Attraction> findByDestinationAndTag(
      @Param("destination") String destination,
      @Param("tag") String tag);

  /**
   * 根据多个标签查找景点
   */
  @Query("SELECT a FROM Attraction a WHERE a.tags && :tags")
  List<Attraction> findByTags(@Param("tags") List<String> tags);
}