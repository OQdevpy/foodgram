import styles from './styles.module.css'

const IngredientsSearch = ({ ingredient, onClick }) => {
  return <div className={styles.container}>
    {ingredient.map(({ name, id, measurement_unit }) => {
      return <div key={id} onClick={_ => onClick({ id, name, measurement_unit })}>{name}</div>
    })}
  </div>
}

export default IngredientsSearch