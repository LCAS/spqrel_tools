#pragma once
#include "defs.h"
#include <deque>
#include <queue>
#include <set>
#include <limits>

  /*!Cell of a distance map.
     Each cell has a row, a column, a parent (which is the closest occupied cell), and a distance (which is a distance to the cell).
   */
  struct DistanceMapCell{
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW;
    //! ctor
    DistanceMapCell(){
      parent = 0;
      distance = std::numeric_limits<int>::max();
      r = 0;
      c = 0;
    }

    //! the closest occupied cell
    DistanceMapCell* parent;
    //! the distance to the closest
    float distance;
    //! row and column
    int r, c;
    //! weight factor for the distance (smaller for nearer objects);
    float weight;

  };

  /*! Distance map structure
    It is a grid of DistanceMapCells, stored as an Eigen Matrix
    A Distance map is a grid that for each cell contains: the distance from the closest occupied cell AND the identity of the closest cell

    The typical use is the following:


    \code{.cpp}
    occupied_cells = ...;// vector of pairs denoting the occupied cells
    // prepare an int image and set all occupied cells
    IntImage input_indices(rows,cols);
    input_indices=-1; // clean the int image
    for(size_t i=0; i<occupied_cells.size(); i++){ 
       const std::pair<int,int> occupied_cell=occupied_cells[i];
       input_indics.at<int>(occupied_cell->first, occupied_cell->second)=i // mark the points in the occupied cells;
    }
    DistanceMap dmap;
    FloatImage distances;
    IntImage   closest_point_indices;

    dmap.compute(closest_point_indices, distances, input_indices, max_distance);

    
    \endcode
    here closest_point_indices is an int_image that contains in the cell [i,j] the index
    (meaning the position in the array) closest to the location i,j, while 
    distances[i,j] contains the distance from the point at i,j and the closest occupied cell.
    max_distance is the squared distance where to stop the expansion
  */
  class DistanceMap : public Eigen::Matrix<DistanceMapCell, Eigen::Dynamic, Eigen::Dynamic>{
  public:
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW;
    int findNeighbors(DistanceMapCell** neighbors, DistanceMapCell* m);

    //! computes a distance map from an int image. The cells in the image having a value >-1 are considered as occupied.
    //! @param imap: an image whose cell [i,j] contains the value of the closest occupied cell, in indexImage. this is overwritten.
    //! @param indexImage: this is the input. Each occupied cell should have a unique value >-1. This value is used to refer to the closest point in the imap
    //! @param maxDistance: stops the expansion at this value.
    void compute(IntImage& imap, FloatImage& distances, 
		 const IntImage& indexImage, float maxDistance = 100);


    //! makes an inage out of a dmap
    void toImage(UnsignedCharImage& img) const;

  };


  //! Queue entry to compute the distance map from an IntImage
  //! It is exposed here to support the construction of different sorts of visit
  //! algorithms, such as Dijkstra or A*

  struct QEntry{
    QEntry(DistanceMapCell* c=0, float d=std::numeric_limits<float>::max()) {
      cell = c;
      distance = d;
    }

    //! comparison operator, returns the closest cell
    inline bool operator < (const QEntry& e) const {
      return e.distance > distance ;
    }

    float distance;
    DistanceMapCell* cell;
  };
  
  //! priority queue of DistanceMapCells, supports several algorithms
  //! it is a sorted container that keeps the entries ordered bu the distance
  struct DistanceMapCellQueue : public std::priority_queue<QEntry> {
    typedef typename std::priority_queue<QEntry>::size_type size_type;
    DistanceMapCellQueue(size_type capacity = 0) { reserve(capacity); };
    inline void reserve(size_type capacity) { this->c.reserve(capacity); } 
    inline size_type capacity() const { return this->c.capacity(); } 
    //! returns the top element of the queue;
    inline DistanceMapCell* top() { return std::priority_queue<QEntry>::top().cell;}
    //! pushes an element in the priority queue
    inline void push(DistanceMapCell* c) { return std::priority_queue<QEntry>::push(QEntry(c, c->distance));}
  };


