#include "distance_map.h"
#include <limits>
#include <deque>
#include <queue>
#include <set>
#include <vector>

using namespace std;

struct DistanceMapCellComparator{
    inline bool operator()(const DistanceMapCell* m1, const DistanceMapCell* m2) const{
        return m1->distance>m2->distance ||
                (m1->distance==m2->distance && m1->r>m2->r) ||
                (m1->distance==m2->distance && m1->r==m2->r && m1->c>m2->c) ;
        return false;
    }
};

int DistanceMap::findNeighbors(DistanceMapCell** neighbors, DistanceMapCell* m){
    int r = m->r;
    int c = m->c;
    int rmin = r-1<0?0:r-1;
    int rmax = r+1>rows()-1?rows()-1:r+1;
    int cmin = c-1<0?0:c-1;
    int cmax = c+1>cols()-1?cols()-1:c+1;
    int k=0;
    for (int rr =rmin; rr<=rmax; rr++)
        for (int cc =cmin; cc<=cmax; cc++) {
            if (rr!=r || cc!=c) {
                neighbors[k]=&(*this)(rr,cc);
                k++;
            }
        }
    return k;
}

void DistanceMap::compute(IntImage& imap,
                          FloatImage& distances,
                          const IntImage& indexImage, float maxDistance){

    // cerr << "A";
    //double t0 = getTime();
    maxDistance *=maxDistance;
    int rows = indexImage.rows;
    int cols = indexImage.cols;
    resize(rows,cols);
    imap.create(rows,cols);
    imap = -1;
    DistanceMapCellQueue q;//(rows*cols);
    //q.reserve(rows*cols);
    for (int r=0; r<indexImage.rows; r++)
        for (int c=0; c<indexImage.cols; c++){
            DistanceMapCell& cell = (*this)(r,c);
            cell.r = r;
            cell.c = c;
            cell.parent = 0;
            cell.distance = maxDistance;
            int idx = indexImage.at<int>(r,c);
            if (idx>-1){
                cell.parent = &cell;
                cell.distance = 0;
                q.push(&cell);
                imap.at<int>(r,c)=idx;
            }
        }
    DistanceMapCell * neighbors[8];
    int operations = 0;
    size_t maxQSize = q.size();
    // cerr << "startq: "  << maxQSize << endl;
    //int currentDistance = 0;
    while (! q.empty()){
        DistanceMapCell* current = q.top();
        DistanceMapCell* parent = current->parent;
        int parentIndex = imap.at<int>(parent->r, parent->c);
        q.pop();
        //if (current->distance<currentDistance)
        //continue;
        //currentDistance = current->distance;
        // // cerr << "current: " << current->r << " "  << current->c << " " << current->distance << " "

        //  	 << "parent: " << parent->r << " "  << parent->c << endl;
        int k = findNeighbors(neighbors, current);
        // // cerr << "neighbors: " << k<< endl;

        for (int i=0; i<k; i++){
            DistanceMapCell* children=  neighbors[i];
            int r = children->r;
            int c = children->c;
            int dr = r-parent->r;
            int dc = c-parent->c;
            int d=(dr*dr+dc*dc);
            // // cerr << "children: " << children->r << " "  << children->c << " " << children->distance <<  " " << d << endl;
            operations++;
            if (d<maxDistance && children->distance>d) {
                children->parent = parent;
                imap.at<int>(r,c) = parentIndex;
                children->distance = d;
                q.push(children);
            }
        }
        maxQSize = maxQSize < q.size() ? q.size() : maxQSize;
    }
    //double t1 = getTime();
    //cerr << "# operations: " << operations << " maxQ: " << maxQSize << " time: " << t1-t0 << endl;

    distances.create(indexImage.rows, indexImage.cols);

    for (int r=0; r<indexImage.rows; r++){
        for (int c=0; c<indexImage.cols; c++){
            DistanceMapCell& mcell = (*this)(r,c);
            float d = std::sqrt(mcell.distance);
            if (indexImage(r,c)<-1)
                d=-d;
            distances.at<float>(r,c)=d;
        }
    }
}

void DistanceMap::toImage(UnsignedCharImage& img) const {
    img.create(rows(), cols());

    float mdist = 0;
    for (int r=0; r<rows(); r++)
        for (int c=0; c<cols(); c++){
            const DistanceMapCell& cell = (*this)(r,c);
            if (cell.distance == std::numeric_limits<float>::max())
                continue;
            mdist = (mdist < cell.distance) ?  cell.distance : mdist;
        }
    mdist = std::sqrt(mdist)
            ;
    // cerr << "mdist=" << mdist;
    for (int r=0; r<rows(); r++)
        for (int c=0; c<cols(); c++){
            const DistanceMapCell& cell = (*this)(r,c);
            float ndist = 127 * std::sqrt(cell.distance)/mdist;
            int v = 127-ndist;
            img.at<unsigned char>(r,c) = (unsigned char) v;
        }
}


